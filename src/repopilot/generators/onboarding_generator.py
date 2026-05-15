"""
Onboarding Generator - Creates onboarding reports for new developers
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class OnboardingGenerator:
    """
    Generates comprehensive onboarding reports including:
    - Project overview
    - Getting started guide
    - Architecture explanation
    - Key components and their purposes
    - Development workflow
    - Common tasks and examples
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.docs_path = project_root / "docs"
        self.docs_path.mkdir(exist_ok=True)

    def generate_onboarding_report(
        self,
        architecture_summary: Dict[str, Any],
        dependency_report: Dict[str, Any],
        coverage_report: Dict[str, Any],
        ast_analyses: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive onboarding report
        
        Args:
            architecture_summary: Architecture analysis results
            dependency_report: Dependency analysis results
            coverage_report: Test coverage analysis results
            ast_analyses: AST analysis results
            
        Returns:
            Markdown formatted onboarding report
        """
        sections = [
            self._generate_header(),
            self._generate_project_overview(architecture_summary),
            self._generate_getting_started(),
            self._generate_architecture_section(architecture_summary, ast_analyses),
            self._generate_key_components(ast_analyses),
            self._generate_dependencies_section(dependency_report),
            self._generate_testing_section(coverage_report),
            self._generate_development_workflow(),
            self._generate_common_tasks(),
            self._generate_resources(),
        ]
        
        return "\n\n".join(sections)

    def _generate_header(self) -> str:
        """Generate report header"""
        return f"""# Developer Onboarding Guide

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Welcome to the project! This guide will help you get up to speed quickly.

---"""

    def _generate_project_overview(self, architecture_summary: Dict[str, Any]) -> str:
        """Generate project overview section"""
        total_files = architecture_summary.get('total_files', 0)
        total_classes = architecture_summary.get('total_classes', 0)
        total_functions = architecture_summary.get('total_functions', 0)
        total_loc = architecture_summary.get('total_lines_of_code', 0)
        
        return f"""## 📋 Project Overview

This project consists of:
- **{total_files}** Python files
- **{total_classes}** classes
- **{total_functions}** functions
- **{total_loc:,}** lines of code

### Project Purpose

This is a Python repository analysis platform that provides:
- Architecture analysis using AST
- Dependency graph generation
- Test coverage recommendations
- Automated documentation generation
- Developer onboarding reports"""

    def _generate_getting_started(self) -> str:
        """Generate getting started section"""
        return """## 🚀 Getting Started

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\\Scripts\\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python -m pytest
   ```

### Quick Start

```python
from repopilot.analyzers import ASTAnalyzer
from pathlib import Path

# Analyze a Python project
analyzer = ASTAnalyzer()
results = analyzer.analyze_directory(Path("./src"))
summary = analyzer.get_architecture_summary()
print(summary)
```"""

    def _generate_architecture_section(
        self,
        architecture_summary: Dict[str, Any],
        ast_analyses: Dict[str, Any]
    ) -> str:
        """Generate architecture explanation section"""
        lines = [
            "## 🏗️ Architecture",
            "",
            "### Project Structure",
            "",
            "```",
            "project/",
            "├── src/",
            "│   └── repopilot/",
            "│       ├── analyzers/      # Code analysis modules",
            "│       ├── generators/     # Documentation generators",
            "│       └── api/            # FastAPI endpoints",
            "├── tests/",
            "│   ├── unit/              # Unit tests",
            "│   └── integration/       # Integration tests",
            "├── docs/                  # Generated documentation",
            "└── pyproject.toml         # Project configuration",
            "```",
            "",
            "### Module Organization",
            "",
        ]
        
        if 'directory_structure' in architecture_summary:
            for directory, files in architecture_summary['directory_structure'].items():
                if 'src' in directory:
                    lines.append(f"**{directory}/**")
                    lines.append("")
                    for file in files[:5]:  # Show first 5 files
                        lines.append(f"- `{file}`")
                    if len(files) > 5:
                        lines.append(f"- ... and {len(files) - 5} more files")
                    lines.append("")
        
        return "\n".join(lines)

    def _generate_key_components(self, ast_analyses: Dict[str, Any]) -> str:
        """Generate key components section"""
        lines = [
            "## 🔑 Key Components",
            "",
            "### Core Analyzers",
            "",
        ]
        
        # Extract key classes from analyses
        key_components = []
        for file_path, analysis in ast_analyses.items():
            if hasattr(analysis, 'classes'):
                for cls in analysis.classes:
                    if not cls.name.startswith('_'):
                        key_components.append({
                            'name': cls.name,
                            'file': file_path,
                            'docstring': cls.docstring,
                            'methods': cls.methods
                        })
        
        for component in key_components[:5]:  # Show top 5 components
            lines.append(f"#### `{component['name']}`")
            lines.append("")
            if component['docstring']:
                # Get first line of docstring
                first_line = component['docstring'].split('\n')[0]
                lines.append(first_line)
            lines.append("")
            lines.append(f"**Location:** `{component['file']}`")
            lines.append("")
            if component['methods']:
                lines.append(f"**Key methods:** {', '.join(component['methods'][:3])}")
                lines.append("")
        
        return "\n".join(lines)

    def _generate_dependencies_section(self, dependency_report: Dict[str, Any]) -> str:
        """Generate dependencies section"""
        lines = [
            "## 📦 Dependencies",
            "",
            f"**Total:** {dependency_report.get('total_dependencies', 0)} dependencies",
            "",
            "### Main External Packages",
            "",
        ]
        
        if 'external_packages_list' in dependency_report:
            for pkg in dependency_report['external_packages_list'][:10]:
                version = pkg.get('version', 'latest')
                lines.append(f"- **{pkg['name']}** ({version})")
        
        lines.extend([
            "",
            "### Standard Library Usage",
            "",
        ])
        
        if 'standard_library_list' in dependency_report:
            stdlib = dependency_report['standard_library_list'][:15]
            lines.append(f"Commonly used: {', '.join(stdlib)}")
        
        return "\n".join(lines)

    def _generate_testing_section(self, coverage_report: Dict[str, Any]) -> str:
        """Generate testing section"""
        overall_coverage = coverage_report.get('overall_coverage', 0)
        total_tests = coverage_report.get('total_tests', 0)
        test_breakdown = coverage_report.get('test_breakdown', {})
        
        lines = [
            "## 🧪 Testing",
            "",
            f"**Overall Coverage:** {overall_coverage}%",
            f"**Total Tests:** {total_tests}",
            "",
            "### Test Distribution",
            "",
            f"- Unit tests: {test_breakdown.get('unit', 0)}",
            f"- Integration tests: {test_breakdown.get('integration', 0)}",
            f"- Functional tests: {test_breakdown.get('functional', 0)}",
            "",
            "### Running Tests",
            "",
            "```bash",
            "# Run all tests",
            "pytest",
            "",
            "# Run with coverage",
            "pytest --cov=src/repopilot --cov-report=html",
            "",
            "# Run specific test file",
            "pytest tests/unit/test_ast_analyzer.py",
            "",
            "# Run tests matching a pattern",
            "pytest -k 'test_analyze'",
            "```",
            "",
        ]
        
        # Add recommendations if available
        if 'recommendations' in coverage_report:
            lines.extend([
                "### Testing Recommendations",
                "",
            ])
            for rec in coverage_report['recommendations']:
                lines.append(f"- {rec}")
        
        return "\n".join(lines)

    def _generate_development_workflow(self) -> str:
        """Generate development workflow section"""
        return """## 💻 Development Workflow

### Code Style

This project follows PEP 8 and uses automated tools:

```bash
# Format code
black src/ tests/

# Check code style
ruff check src/ tests/

# Type checking
mypy src/
```

### Git Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Run tests before pushing:**
   ```bash
   pytest
   ```

4. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks"""

    def _generate_common_tasks(self) -> str:
        """Generate common tasks section"""
        return """## 📝 Common Tasks

### Adding a New Analyzer

1. Create a new file in `src/repopilot/analyzers/`
2. Implement the analyzer class
3. Add it to `src/repopilot/analyzers/__init__.py`
4. Write unit tests in `tests/unit/`
5. Update documentation

### Adding a New API Endpoint

1. Add the endpoint in `src/repopilot/api/main.py`
2. Define request/response models using Pydantic
3. Add integration tests
4. Update API documentation

### Debugging Tips

- Use `python -m pdb` for debugging
- Add logging statements using the `logging` module
- Run tests with `-v` flag for verbose output
- Use `pytest --pdb` to drop into debugger on failures"""

    def _generate_resources(self) -> str:
        """Generate resources section"""
        return """## 📚 Resources

### Documentation

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)

### Project Documentation

- `docs/ARCHITECTURE.md` - Detailed architecture documentation
- `docs/API.md` - API endpoint documentation
- `docs/MODULES.md` - Module documentation

### Getting Help

- Check existing issues on GitHub
- Review the documentation in the `docs/` directory
- Ask questions in team chat
- Pair with experienced team members

---

**Happy coding! 🎉**"""

    def save_onboarding_report(self, content: str) -> Path:
        """
        Save onboarding report to file
        
        Args:
            content: Report content
            
        Returns:
            Path to saved file
        """
        file_path = self.docs_path / "ONBOARDING.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

# Made with Bob
