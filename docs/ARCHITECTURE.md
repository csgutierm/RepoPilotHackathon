# RepoPilot Architecture Documentation

## Overview

RepoPilot is a Python repository analysis platform built with a modular architecture that separates concerns into distinct layers: analyzers, generators, and API.

## Architecture Principles

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Separation of Concerns**: Analysis, generation, and API layers are independent
3. **Extensibility**: New analyzers and generators can be added easily
4. **Type Safety**: Strong typing with Python 3.13+ type hints
5. **Clean Code**: Following PEP 8 and modern Python best practices

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│                     (FastAPI REST API)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Analyzers   │  │  Generators  │  │   Utilities  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│         (File System, AST, Configuration Files)              │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Analyzers Module (`src/repopilot/analyzers/`)

The analyzers module contains components that extract information from Python repositories.

#### ASTAnalyzer (`ast_analyzer.py`)

**Purpose**: Analyzes Python source code using Abstract Syntax Trees

**Key Responsibilities**:
- Parse Python files into AST
- Extract classes, functions, and methods
- Calculate code metrics (LOC, complexity)
- Generate architecture summaries

**Data Flow**:
```
Python Files → AST Parser → Node Visitor → Data Extraction → FileAnalysis
```

**Key Classes**:
- `ASTAnalyzer`: Main analyzer class
- `FileAnalysis`: Container for file analysis results
- `ClassInfo`: Class metadata
- `FunctionInfo`: Function metadata
- `ImportInfo`: Import statement metadata

**Design Patterns**:
- **Visitor Pattern**: Traverses AST nodes
- **Data Class Pattern**: Immutable data containers
- **Builder Pattern**: Constructs complex analysis objects

#### DependencyAnalyzer (`dependency_analyzer.py`)

**Purpose**: Analyzes project dependencies and their relationships

**Key Responsibilities**:
- Parse requirements.txt and pyproject.toml
- Extract import statements from code
- Build dependency graphs
- Distinguish between standard library, external, and local modules

**Data Flow**:
```
Config Files → Parser → Dependency Info
Python Files → Import Extractor → Module Dependencies → Dependency Graph
```

**Key Classes**:
- `DependencyAnalyzer`: Main analyzer class
- `DependencyInfo`: Dependency metadata
- `ModuleDependency`: Module relationship metadata

**Design Patterns**:
- **Strategy Pattern**: Different parsing strategies for different file types
- **Graph Pattern**: Dependency graph construction

#### CoverageAnalyzer (`coverage_analyzer.py`)

**Purpose**: Analyzes test coverage and provides recommendations

**Key Responsibilities**:
- Identify test files and test functions
- Match tests to source code
- Calculate coverage percentages
- Generate test recommendations

**Data Flow**:
```
Test Files → Test Extractor → TestInfo
Source Files → Code Extractor → ModuleCoverage
TestInfo + ModuleCoverage → Coverage Calculator → Coverage Report
```

**Key Classes**:
- `CoverageAnalyzer`: Main analyzer class
- `TestInfo`: Test metadata
- `ModuleCoverage`: Coverage information per module

**Design Patterns**:
- **Template Method Pattern**: Analysis workflow
- **Strategy Pattern**: Different test type detection strategies

### 2. Generators Module (`src/repopilot/generators/`)

The generators module creates documentation and reports from analysis results.

#### DocGenerator (`doc_generator.py`)

**Purpose**: Generates various types of documentation

**Key Responsibilities**:
- Generate module documentation from AST analysis
- Create API documentation
- Generate architecture documentation
- Create dependency documentation
- Generate README files

**Output Formats**:
- Markdown (.md)
- Structured text

**Key Classes**:
- `DocGenerator`: Main generator class

**Design Patterns**:
- **Template Method Pattern**: Documentation generation workflow
- **Builder Pattern**: Constructs complex documentation

#### OnboardingGenerator (`onboarding_generator.py`)

**Purpose**: Creates comprehensive onboarding reports for new developers

**Key Responsibilities**:
- Generate project overviews
- Create getting started guides
- Explain architecture
- Document key components
- Provide development workflows

**Key Classes**:
- `OnboardingGenerator`: Main generator class

**Design Patterns**:
- **Composite Pattern**: Combines multiple documentation sections
- **Template Method Pattern**: Report generation workflow

### 3. API Module (`src/repopilot/api/`)

The API module provides REST endpoints for accessing RepoPilot functionality.

#### FastAPI Application (`main.py`)

**Purpose**: Provides HTTP REST API interface

**Key Responsibilities**:
- Handle HTTP requests and responses
- Validate input data
- Coordinate analyzer and generator operations
- Return structured JSON responses

**Endpoints**:
- Analysis endpoints (`/analyze/*`)
- Generation endpoints (`/generate/*`)
- Utility endpoints (`/health`, `/info`)

**Key Components**:
- Pydantic models for request/response validation
- FastAPI route handlers
- Error handling middleware

**Design Patterns**:
- **MVC Pattern**: Model-View-Controller architecture
- **Dependency Injection**: FastAPI's dependency system
- **Decorator Pattern**: Route decorators

## Data Models

### Core Data Structures

```python
@dataclass
class FileAnalysis:
    file_path: str
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[ImportInfo]
    lines_of_code: int
    docstring: Optional[str]
    complexity_score: int

@dataclass
class ClassInfo:
    name: str
    line_number: int
    methods: List[str]
    bases: List[str]
    docstring: Optional[str]

@dataclass
class FunctionInfo:
    name: str
    line_number: int
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    is_async: bool
```

### API Models

```python
class AnalysisRequest(BaseModel):
    repository_path: str

class AnalysisResponse(BaseModel):
    status: str
    architecture_summary: Dict[str, Any]
    dependency_report: Dict[str, Any]
    coverage_report: Dict[str, Any]
    message: str
```

## Design Decisions

### 1. AST-Based Analysis

**Decision**: Use Python's built-in `ast` module for code analysis

**Rationale**:
- Native Python support, no external dependencies
- Accurate parsing of Python syntax
- Access to detailed code structure information
- Better than regex-based parsing

**Trade-offs**:
- Only works with syntactically valid Python code
- Requires Python runtime for analysis

### 2. Modular Architecture

**Decision**: Separate analyzers, generators, and API into distinct modules

**Rationale**:
- Single Responsibility Principle
- Easy to test individual components
- Extensible - new analyzers can be added
- Reusable - components can be used independently

**Trade-offs**:
- More complex project structure
- Requires coordination between modules

### 3. FastAPI for REST API

**Decision**: Use FastAPI instead of Flask or Django

**Rationale**:
- Automatic API documentation generation
- Built-in request/response validation with Pydantic
- High performance (async support)
- Modern Python features (type hints)

**Trade-offs**:
- Newer framework, smaller ecosystem than Flask/Django
- Learning curve for developers unfamiliar with async Python

### 4. Dataclasses for Data Models

**Decision**: Use Python dataclasses for internal data structures

**Rationale**:
- Immutable by default (with frozen=True)
- Automatic __init__, __repr__, __eq__ methods
- Type hints support
- Clean, readable code

**Trade-offs**:
- Python 3.7+ requirement
- Less flexible than regular classes

### 5. Type Hints Throughout

**Decision**: Use comprehensive type hints with mypy checking

**Rationale**:
- Better IDE support and autocomplete
- Catch type-related bugs early
- Self-documenting code
- Better maintainability

**Trade-offs**:
- Additional development overhead
- Requires mypy in CI/CD pipeline

## Extension Points

### Adding New Analyzers

1. Create new analyzer class in `src/repopilot/analyzers/`
2. Implement required interface methods
3. Add to `__init__.py` exports
4. Create corresponding tests
5. Update API endpoints if needed

### Adding New Generators

1. Create new generator class in `src/repopilot/generators/`
2. Implement generation methods
3. Add to `__init__.py` exports
4. Create corresponding tests
5. Add API endpoint if needed

### Adding New API Endpoints

1. Define Pydantic models for request/response
2. Add route handler in `main.py`
3. Add error handling
4. Create integration tests
5. Update API documentation

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic
- Located in `tests/unit/`

### Integration Tests
- Test component interactions
- Test API endpoints end-to-end
- Use real file system with temporary directories
- Located in `tests/integration/`

### Test Structure
```
tests/
├── unit/
│   ├── test_ast_analyzer.py
│   ├── test_dependency_analyzer.py
│   └── test_coverage_analyzer.py
└── integration/
    └── test_api.py
```

## Performance Considerations

### AST Analysis
- **Caching**: Analysis results are cached in memory
- **Lazy Loading**: Files are analyzed on-demand
- **Parallel Processing**: Could be added for large repositories

### Memory Usage
- **Streaming**: Large files could be processed in chunks
- **Cleanup**: Temporary data is cleaned up after analysis

### API Performance
- **Async**: FastAPI supports async operations
- **Caching**: Results could be cached with Redis
- **Rate Limiting**: Could be added for production use

## Security Considerations

### Input Validation
- All API inputs are validated with Pydantic
- File paths are validated to prevent directory traversal
- Repository paths must exist and be directories

### Code Execution
- No arbitrary code execution
- Only static analysis using AST
- Safe parsing of configuration files

## Deployment Architecture

### Development
```
Developer Machine
├── Python 3.13+
├── Virtual Environment
├── Source Code
└── Local Testing
```

### Production (Recommended)
```
Container Environment
├── Docker Container
│   ├── Python 3.13 Runtime
│   ├── RepoPilot Application
│   └── Dependencies
├── Reverse Proxy (nginx)
├── Load Balancer (optional)
└── Monitoring & Logging
```

## Future Enhancements

### Planned Features
1. **Plugin System**: Allow third-party analyzers
2. **Database Storage**: Persist analysis results
3. **Web UI**: Browser-based interface
4. **CI/CD Integration**: GitHub Actions, GitLab CI
5. **Advanced Metrics**: Code quality scores, technical debt

### Scalability Improvements
1. **Distributed Processing**: Analyze large repositories in parallel
2. **Caching Layer**: Redis for result caching
3. **Queue System**: Background job processing
4. **Microservices**: Split into smaller services

## Conclusion

RepoPilot's architecture is designed for maintainability, extensibility, and performance. The modular design allows for easy testing and future enhancements while providing a clean separation of concerns. The use of modern Python features and frameworks ensures the codebase remains current and developer-friendly.