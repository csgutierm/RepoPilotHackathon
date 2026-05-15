"""
Documentation Generator - Generates documentation from code analysis
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DocGenerator:
    """
    Generates documentation including:
    - Module documentation
    - API documentation
    - Architecture overview
    - Code examples
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.docs_path = project_root / "docs"
        self.docs_path.mkdir(exist_ok=True)

    def generate_module_docs(self, ast_analysis: Dict[str, Any]) -> str:
        """
        Generate module documentation from AST analysis
        
        Args:
            ast_analysis: Dictionary with AST analysis results
            
        Returns:
            Markdown formatted documentation
        """
        lines = [
            "# Module Documentation",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            "",
            f"Total files analyzed: {len(ast_analysis)}",
            "",
        ]
        
        for file_path, analysis in ast_analysis.items():
            lines.extend(self._generate_file_documentation(file_path, analysis))
        
        return "\n".join(lines)

    def _generate_file_documentation(self, file_path: str, analysis: Any) -> List[str]:
        """Generate documentation for a single file"""
        lines = [
            f"## {file_path}",
            "",
        ]
        
        if hasattr(analysis, 'docstring') and analysis.docstring:
            lines.extend([
                "### Description",
                "",
                analysis.docstring,
                "",
            ])
        
        # Document classes
        if hasattr(analysis, 'classes') and analysis.classes:
            lines.extend([
                "### Classes",
                "",
            ])
            
            for cls in analysis.classes:
                lines.extend(self._generate_class_documentation(cls))
        
        # Document functions
        if hasattr(analysis, 'functions') and analysis.functions:
            lines.extend([
                "### Functions",
                "",
            ])
            
            for func in analysis.functions:
                lines.extend(self._generate_function_documentation(func))
        
        lines.append("")
        return lines

    def _generate_class_documentation(self, cls: Any) -> List[str]:
        """Generate documentation for a class"""
        lines = [
            f"#### `{cls.name}`",
            "",
        ]
        
        if cls.bases:
            lines.append(f"**Inherits from:** {', '.join(cls.bases)}")
            lines.append("")
        
        if cls.docstring:
            lines.append(cls.docstring)
            lines.append("")
        
        if cls.methods:
            lines.append("**Methods:**")
            lines.append("")
            for method in cls.methods:
                lines.append(f"- `{method}()`")
            lines.append("")
        
        return lines

    def _generate_function_documentation(self, func: Any) -> List[str]:
        """Generate documentation for a function"""
        lines = [
            f"#### `{func.name}({', '.join(func.args)})`",
            "",
        ]
        
        if func.is_async:
            lines.insert(1, "*Async function*")
            lines.insert(2, "")
        
        if func.docstring:
            lines.append(func.docstring)
            lines.append("")
        
        if func.returns:
            lines.append(f"**Returns:** `{func.returns}`")
            lines.append("")
        
        return lines

    def generate_api_docs(self, endpoints: List[Dict[str, Any]]) -> str:
        """
        Generate API documentation
        
        Args:
            endpoints: List of API endpoint information
            
        Returns:
            Markdown formatted API documentation
        """
        lines = [
            "# API Documentation",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Endpoints",
            "",
        ]
        
        for endpoint in endpoints:
            lines.extend(self._generate_endpoint_documentation(endpoint))
        
        return "\n".join(lines)

    def _generate_endpoint_documentation(self, endpoint: Dict[str, Any]) -> List[str]:
        """Generate documentation for an API endpoint"""
        lines = [
            f"### {endpoint.get('method', 'GET')} `{endpoint.get('path', '/')}`",
            "",
        ]
        
        if 'description' in endpoint:
            lines.append(endpoint['description'])
            lines.append("")
        
        if 'parameters' in endpoint:
            lines.extend([
                "**Parameters:**",
                "",
            ])
            for param in endpoint['parameters']:
                lines.append(f"- `{param['name']}` ({param['type']}): {param.get('description', '')}")
            lines.append("")
        
        if 'response' in endpoint:
            lines.extend([
                "**Response:**",
                "",
                "```json",
                str(endpoint['response']),
                "```",
                "",
            ])
        
        return lines

    def generate_architecture_docs(self, architecture_summary: Dict[str, Any]) -> str:
        """
        Generate architecture documentation
        
        Args:
            architecture_summary: Dictionary with architecture information
            
        Returns:
            Markdown formatted architecture documentation
        """
        lines = [
            "# Architecture Documentation",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Project Overview",
            "",
            f"- **Total Files:** {architecture_summary.get('total_files', 0)}",
            f"- **Total Classes:** {architecture_summary.get('total_classes', 0)}",
            f"- **Total Functions:** {architecture_summary.get('total_functions', 0)}",
            f"- **Total Lines of Code:** {architecture_summary.get('total_lines_of_code', 0)}",
            f"- **Average Complexity:** {architecture_summary.get('average_complexity', 0)}",
            "",
            "## Directory Structure",
            "",
        ]
        
        if 'directory_structure' in architecture_summary:
            for directory, files in architecture_summary['directory_structure'].items():
                lines.append(f"### {directory}")
                lines.append("")
                for file in files:
                    lines.append(f"- {file}")
                lines.append("")
        
        return "\n".join(lines)

    def generate_dependency_docs(self, dependency_report: Dict[str, Any]) -> str:
        """
        Generate dependency documentation
        
        Args:
            dependency_report: Dictionary with dependency information
            
        Returns:
            Markdown formatted dependency documentation
        """
        lines = [
            "# Dependency Documentation",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- **Total Dependencies:** {dependency_report.get('total_dependencies', 0)}",
            f"- **External Packages:** {dependency_report.get('external_packages', 0)}",
            f"- **Standard Library Modules:** {dependency_report.get('standard_library', 0)}",
            "",
            "## External Packages",
            "",
        ]
        
        if 'external_packages_list' in dependency_report:
            lines.append("| Package | Version | Used In |")
            lines.append("|---------|---------|---------|")
            
            for pkg in dependency_report['external_packages_list']:
                version = pkg.get('version', 'N/A')
                used_count = len(pkg.get('used_in_files', []))
                lines.append(f"| {pkg['name']} | {version} | {used_count} files |")
            
            lines.append("")
        
        if 'standard_library_list' in dependency_report:
            lines.extend([
                "## Standard Library Modules",
                "",
            ])
            
            stdlib_modules = dependency_report['standard_library_list']
            # Group in rows of 5
            for i in range(0, len(stdlib_modules), 5):
                row = stdlib_modules[i:i+5]
                lines.append(f"- {', '.join(row)}")
            
            lines.append("")
        
        return "\n".join(lines)

    def save_documentation(self, filename: str, content: str) -> Path:
        """
        Save documentation to a file
        
        Args:
            filename: Name of the file (without path)
            content: Documentation content
            
        Returns:
            Path to the saved file
        """
        file_path = self.docs_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

    def generate_readme(self, project_info: Dict[str, Any]) -> str:
        """
        Generate a README.md file
        
        Args:
            project_info: Dictionary with project information
            
        Returns:
            Markdown formatted README content
        """
        lines = [
            f"# {project_info.get('name', 'Project')}",
            "",
            project_info.get('description', 'A Python project'),
            "",
            "## Installation",
            "",
            "```bash",
            "pip install -r requirements.txt",
            "```",
            "",
            "## Usage",
            "",
            "```python",
            f"from {project_info.get('package_name', 'project')} import main",
            "",
            "# Your code here",
            "```",
            "",
            "## Project Structure",
            "",
        ]
        
        if 'structure' in project_info:
            for item in project_info['structure']:
                lines.append(f"- {item}")
            lines.append("")
        
        lines.extend([
            "## Development",
            "",
            "### Running Tests",
            "",
            "```bash",
            "pytest",
            "```",
            "",
            "### Code Quality",
            "",
            "```bash",
            "# Format code",
            "black .",
            "",
            "# Lint code",
            "ruff check .",
            "",
            "# Type checking",
            "mypy .",
            "```",
            "",
            "## Documentation",
            "",
            "See the `docs/` directory for detailed documentation.",
            "",
            "## License",
            "",
            project_info.get('license', 'MIT'),
            "",
        ])
        
        return "\n".join(lines)

# Made with Bob
