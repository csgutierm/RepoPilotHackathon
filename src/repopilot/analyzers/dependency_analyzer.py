"""
Dependency Analyzer - Analyzes project dependencies and their relationships
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DependencyInfo:
    """Information about a dependency"""
    name: str
    version: Optional[str] = None
    is_standard_lib: bool = False
    is_local: bool = False
    used_in_files: List[str] = field(default_factory=list)


@dataclass
class ModuleDependency:
    """Represents a dependency between modules"""
    source_module: str
    target_module: str
    import_type: str  # 'import' or 'from'


class DependencyAnalyzer:
    """
    Analyzes project dependencies including:
    - External packages (from requirements.txt, pyproject.toml)
    - Internal module dependencies
    - Standard library usage
    - Dependency graph generation
    """

    # Common Python standard library modules
    STDLIB_MODULES = {
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'concurrent',
        'contextlib', 'copy', 'csv', 'dataclasses', 'datetime', 'decimal', 'enum',
        'functools', 'glob', 'hashlib', 'http', 'io', 'itertools', 'json', 'logging',
        'math', 'os', 'pathlib', 'pickle', 're', 'shutil', 'socket', 'sqlite3',
        'string', 'subprocess', 'sys', 'tempfile', 'threading', 'time', 'typing',
        'unittest', 'urllib', 'uuid', 'warnings', 'weakref', 'xml', 'zipfile'
    }

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.dependencies: Dict[str, DependencyInfo] = {}
        self.module_dependencies: List[ModuleDependency] = []
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)

    def analyze_project(self) -> Dict[str, Any]:
        """
        Perform complete dependency analysis of the project
        
        Returns:
            Dictionary with dependency information and graph
        """
        # Analyze package dependencies
        self._analyze_requirements()
        self._analyze_pyproject()
        
        # Analyze code imports
        self._analyze_imports()
        
        # Build dependency graph
        self._build_dependency_graph()
        
        return self.get_dependency_report()

    def _analyze_requirements(self) -> None:
        """Parse requirements.txt file"""
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            return
        
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self._parse_requirement_line(line)
        except Exception as e:
            print(f"Warning: Could not parse requirements.txt: {str(e)}")

    def _analyze_pyproject(self) -> None:
        """Parse pyproject.toml file for dependencies"""
        pyproject_file = self.project_root / "pyproject.toml"
        if not pyproject_file.exists():
            return
        
        try:
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple regex-based parsing for dependencies
            # In production, use tomli/tomllib
            dep_pattern = r'"([a-zA-Z0-9_-]+)(?:>=|==|~=|>|<)([0-9.]+)"'
            matches = re.findall(dep_pattern, content)
            
            for name, version in matches:
                if name not in self.dependencies:
                    self.dependencies[name] = DependencyInfo(
                        name=name,
                        version=version,
                        is_standard_lib=False,
                        is_local=False
                    )
        except Exception as e:
            print(f"Warning: Could not parse pyproject.toml: {str(e)}")

    def _parse_requirement_line(self, line: str) -> None:
        """Parse a single requirement line"""
        # Remove comments
        line = line.split('#')[0].strip()
        if not line:
            return
        
        # Parse package name and version
        match = re.match(r'([a-zA-Z0-9_-]+)(?:\[.*\])?(?:>=|==|~=|>|<)?([0-9.]*)', line)
        if match:
            name, version = match.groups()
            if name not in self.dependencies:
                self.dependencies[name] = DependencyInfo(
                    name=name,
                    version=version if version else None,
                    is_standard_lib=False,
                    is_local=False
                )

    def _analyze_imports(self) -> None:
        """Analyze all Python files for import statements"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                self._analyze_file_imports(file_path)
            except Exception as e:
                print(f"Warning: Could not analyze imports in {file_path}: {str(e)}")

    def _analyze_file_imports(self, file_path: Path) -> None:
        """Analyze imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            relative_path = str(file_path.relative_to(self.project_root))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._process_import(alias.name, relative_path, 'import')
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._process_import(node.module, relative_path, 'from')
                        
        except Exception as e:
            raise ValueError(f"Error analyzing imports in {file_path}: {str(e)}")

    def _process_import(self, module_name: str, file_path: str, import_type: str) -> None:
        """Process a single import statement"""
        # Get the top-level package name
        top_level = module_name.split('.')[0]
        
        # Determine if it's standard library, local, or external
        is_stdlib = top_level in self.STDLIB_MODULES
        is_local = self._is_local_module(module_name)
        
        if not is_local:
            # Track external/stdlib dependency
            if top_level not in self.dependencies:
                self.dependencies[top_level] = DependencyInfo(
                    name=top_level,
                    is_standard_lib=is_stdlib,
                    is_local=False
                )
            
            if file_path not in self.dependencies[top_level].used_in_files:
                self.dependencies[top_level].used_in_files.append(file_path)
        
        # Track module dependencies for graph
        source_module = self._get_module_name(file_path)
        self.module_dependencies.append(
            ModuleDependency(
                source_module=source_module,
                target_module=module_name,
                import_type=import_type
            )
        )

    def _is_local_module(self, module_name: str) -> bool:
        """Check if a module is part of the local project"""
        # Check if module starts with project package name
        src_path = self.project_root / "src"
        if src_path.exists():
            for item in src_path.iterdir():
                if item.is_dir() and module_name.startswith(item.name):
                    return True
        return False

    def _get_module_name(self, file_path: str) -> str:
        """Convert file path to module name"""
        # Remove .py extension and convert path separators to dots
        module = file_path.replace('\\', '/').replace('.py', '')
        # Remove src/ prefix if present
        if module.startswith('src/'):
            module = module[4:]
        return module.replace('/', '.')

    def _build_dependency_graph(self) -> None:
        """Build a dependency graph from module dependencies"""
        for dep in self.module_dependencies:
            self.dependency_graph[dep.source_module].add(dep.target_module)

    def get_dependency_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive dependency report
        
        Returns:
            Dictionary with dependency analysis results
        """
        external_deps = [
            dep for dep in self.dependencies.values()
            if not dep.is_standard_lib and not dep.is_local
        ]
        
        stdlib_deps = [
            dep for dep in self.dependencies.values()
            if dep.is_standard_lib
        ]
        
        return {
            "total_dependencies": len(self.dependencies),
            "external_packages": len(external_deps),
            "standard_library": len(stdlib_deps),
            "external_packages_list": [
                {
                    "name": dep.name,
                    "version": dep.version,
                    "used_in_files": dep.used_in_files
                }
                for dep in external_deps
            ],
            "standard_library_list": [dep.name for dep in stdlib_deps],
            "module_dependencies": [
                {
                    "source": dep.source_module,
                    "target": dep.target_module,
                    "type": dep.import_type
                }
                for dep in self.module_dependencies
            ],
            "dependency_graph": {
                module: list(deps)
                for module, deps in self.dependency_graph.items()
            }
        }

    def get_dependency_graph_dot(self) -> str:
        """
        Generate a DOT format graph for visualization
        
        Returns:
            DOT format string
        """
        lines = ["digraph Dependencies {", "  rankdir=LR;", "  node [shape=box];", ""]
        
        for source, targets in self.dependency_graph.items():
            source_clean = source.replace('.', '_')
            for target in targets:
                target_clean = target.replace('.', '_')
                lines.append(f'  "{source_clean}" -> "{target_clean}";')
        
        lines.append("}")
        return "\n".join(lines)

# Made with Bob
