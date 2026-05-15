# RepoPilot 🚀

A powerful Python repository analysis platform that provides comprehensive insights into your codebase through AST-based analysis, dependency mapping, test coverage recommendations, and automated documentation generation.

## 📋 Features

- **Architecture Analysis**: Deep code analysis using Python's Abstract Syntax Tree (AST)
- **Dependency Mapping**: Visualize and understand project dependencies
- **Test Coverage Analysis**: Identify untested code and get recommendations
- **Documentation Generation**: Automatically generate comprehensive documentation
- **Onboarding Reports**: Create developer-friendly onboarding guides
- **REST API**: FastAPI-based API for easy integration

## 🎯 Project Goals

RepoPilot helps development teams:
- Understand complex codebases quickly
- Identify architectural patterns and anti-patterns
- Track dependencies and their relationships
- Improve test coverage systematically
- Onboard new developers efficiently

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd RepoPilotHackathon
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### As a Python Library

```python
from pathlib import Path
from repopilot.analyzers import ASTAnalyzer, DependencyAnalyzer, CoverageAnalyzer
from repopilot.generators import DocGenerator, OnboardingGenerator

# Analyze a repository
repo_path = Path("./your-project")

# AST Analysis
ast_analyzer = ASTAnalyzer()
ast_analyzer.analyze_directory(repo_path)
architecture = ast_analyzer.get_architecture_summary()
print(f"Total files: {architecture['total_files']}")
print(f"Total classes: {architecture['total_classes']}")

# Dependency Analysis
dep_analyzer = DependencyAnalyzer(repo_path)
dependencies = dep_analyzer.analyze_project()
print(f"Total dependencies: {dependencies['total_dependencies']}")

# Coverage Analysis
coverage_analyzer = CoverageAnalyzer(repo_path)
coverage = coverage_analyzer.analyze_coverage()
print(f"Overall coverage: {coverage['overall_coverage']}%")

# Generate Documentation
doc_gen = DocGenerator(repo_path)
arch_doc = doc_gen.generate_architecture_docs(architecture)
doc_gen.save_documentation("ARCHITECTURE.md", arch_doc)

# Generate Onboarding Report
onboarding_gen = OnboardingGenerator(repo_path)
report = onboarding_gen.generate_onboarding_report(
    architecture, dependencies, coverage, ast_analyzer.analyses
)
onboarding_gen.save_onboarding_report(report)
```

#### As a Visual Dashboard (Recommended)

1. **Start the Streamlit dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

2. **Access the dashboard:**
   - Open your browser to: http://localhost:8501
   - Enter the repository path in the sidebar
   - Click "Analyze Repository" to start

3. **Features:**
   - 🏗️ **Architecture Tab**: Interactive visualizations of code structure, complexity metrics, and module breakdown
   - 🔗 **Dependencies Tab**: Dependency distribution charts, external packages list, and module dependency graphs
   - 🎯 **Coverage Tab**: Coverage gauges, test type distribution, and module-level coverage details
   - 📊 **Summary Tab**: Complete overview with export options for documentation and onboarding reports

#### As a REST API

1. **Start the API server:**
   ```bash
   python -m uvicorn src.repopilot.api.main:app --reload
   ```

2. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Example API calls:**

   ```bash
   # Analyze a repository
   curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"repository_path": "./your-project"}'
   
   # Generate documentation
   curl -X POST "http://localhost:8000/generate/documentation" \
     -H "Content-Type: application/json" \
     -d '{"repository_path": "./your-project", "include_architecture": true}'
   
   # Generate onboarding report
   curl -X POST "http://localhost:8000/generate/onboarding" \
     -H "Content-Type: application/json" \
     -d '{"repository_path": "./your-project"}'
   ```

## 📁 Project Structure

```
RepoPilotHackathon/
├── src/
│   └── repopilot/
│       ├── analyzers/           # Analysis modules
│       │   ├── ast_analyzer.py          # AST-based code analysis
│       │   ├── dependency_analyzer.py   # Dependency mapping
│       │   └── coverage_analyzer.py     # Test coverage analysis
│       ├── generators/          # Documentation generators
│       │   ├── doc_generator.py         # Documentation generation
│       │   └── onboarding_generator.py  # Onboarding reports
│       └── api/                 # FastAPI application
│           └── main.py                  # API endpoints
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── docs/                        # Generated documentation
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/repopilot --cov-report=html

# Run specific test file
pytest tests/unit/test_ast_analyzer.py

# Run tests with verbose output
pytest -v
```

## 🛠️ Development

### Code Quality

This project uses automated tools for code quality:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

## 📚 Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md) - Detailed architecture overview
- [API Documentation](http://localhost:8000/docs) - Interactive API documentation
- [Onboarding Guide](docs/ONBOARDING.md) - Developer onboarding guide

## 🔧 Configuration

### pyproject.toml

The project uses `pyproject.toml` for configuration. Key settings:

- Python version: 3.13+
- Testing: pytest with coverage
- Code formatting: black
- Linting: ruff
- Type checking: mypy

## 📊 Analysis Capabilities

### AST Analysis
- Extract classes, functions, and methods
- Analyze code structure and complexity
- Generate architecture summaries
- Calculate cyclomatic complexity

### Dependency Analysis
- Parse requirements.txt and pyproject.toml
- Identify external packages and versions
- Map internal module dependencies
- Generate dependency graphs (DOT format)
- Distinguish between standard library and external packages

### Coverage Analysis
- Identify tested vs untested code
- Calculate coverage percentages per module
- Provide test recommendations
- Classify tests (unit, integration, functional)

### Documentation Generation
- Module documentation from docstrings
- API documentation
- Architecture overviews
- Dependency documentation

### Onboarding Reports
- Project overview and statistics
- Getting started guides
- Architecture explanations
- Key components documentation
- Development workflow guides

## 🚀 API Endpoints

### Analysis Endpoints
- `POST /analyze` - Complete repository analysis
- `POST /analyze/architecture` - Architecture analysis only
- `POST /analyze/dependencies` - Dependency analysis only
- `POST /analyze/coverage` - Coverage analysis only

### Generation Endpoints
- `POST /generate/documentation` - Generate documentation
- `POST /generate/onboarding` - Generate onboarding report

### Utility Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /info` - Detailed API information

## 🤝 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation in the `docs/` directory
- Review existing issues and pull requests

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [pytest](https://docs.pytest.org/) - Testing framework
- Python's built-in `ast` module - Code analysis

---

**Made with ❤️ for developers who want to understand their code better**