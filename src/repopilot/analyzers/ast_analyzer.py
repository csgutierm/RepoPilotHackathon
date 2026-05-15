"""
AST Analyzer - Analyzes Python code using Abstract Syntax Trees
"""

import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ClassInfo:
    """Information about a class definition"""
    name: str
    line_number: int
    methods: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class FunctionInfo:
    """Information about a function definition"""
    name: str
    line_number: int
    args: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    docstring: Optional[str] = None
    is_async: bool = False


@dataclass
class ImportInfo:
    """Information about imports"""
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    line_number: int = 0


@dataclass
class FileAnalysis:
    """Complete analysis of a Python file"""
    file_path: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    lines_of_code: int = 0
    docstring: Optional[str] = None
    complexity_score: int = 0


class ASTAnalyzer:
    """
    Analyzes Python source code using AST to extract:
    - Classes and their methods
    - Functions and their signatures
    - Import statements
    - Code metrics (LOC, complexity)
    """

    def __init__(self) -> None:
        self.analyses: Dict[str, FileAnalysis] = {}

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """
        Analyze a single Python file
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            FileAnalysis object with extracted information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=str(file_path))
            
            analysis = FileAnalysis(file_path=str(file_path))
            analysis.docstring = ast.get_docstring(tree)
            analysis.lines_of_code = len(source_code.splitlines())
            
            # Extract information from AST
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis.classes.append(self._extract_class_info(node))
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Only top-level functions (not methods)
                    if self._is_top_level_function(tree, node):
                        analysis.functions.append(self._extract_function_info(node))
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis.imports.append(self._extract_import_info(node))
            
            # Calculate complexity score
            analysis.complexity_score = self._calculate_complexity(tree)
            
            self.analyses[str(file_path)] = analysis
            return analysis
            
        except Exception as e:
            raise ValueError(f"Error analyzing file {file_path}: {str(e)}")

    def analyze_directory(self, directory_path: Path) -> Dict[str, FileAnalysis]:
        """
        Analyze all Python files in a directory recursively
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Dictionary mapping file paths to their analyses
        """
        python_files = list(directory_path.rglob("*.py"))
        
        for file_path in python_files:
            try:
                self.analyze_file(file_path)
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {str(e)}")
        
        return self.analyses

    def get_architecture_summary(self) -> Dict[str, Any]:
        """
        Generate a high-level architecture summary
        
        Returns:
            Dictionary with architecture metrics and structure
        """
        total_files = len(self.analyses)
        total_classes = sum(len(a.classes) for a in self.analyses.values())
        total_functions = sum(len(a.functions) for a in self.analyses.values())
        total_loc = sum(a.lines_of_code for a in self.analyses.values())
        avg_complexity = (
            sum(a.complexity_score for a in self.analyses.values()) / total_files
            if total_files > 0 else 0
        )
        
        # Group files by directory
        directory_structure: Dict[str, List[str]] = {}
        for file_path in self.analyses.keys():
            directory = str(Path(file_path).parent)
            if directory not in directory_structure:
                directory_structure[directory] = []
            directory_structure[directory].append(Path(file_path).name)
        
        return {
            "total_files": total_files,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "total_lines_of_code": total_loc,
            "average_complexity": round(avg_complexity, 2),
            "directory_structure": directory_structure,
            "files_analyzed": list(self.analyses.keys()),
        }

    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from a class definition"""
        methods = [
            m.name for m in node.body 
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        bases = [self._get_name(base) for base in node.bases]
        
        return ClassInfo(
            name=node.name,
            line_number=node.lineno,
            methods=methods,
            bases=bases,
            docstring=ast.get_docstring(node)
        )

    def _extract_function_info(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        """Extract information from a function definition"""
        args = [arg.arg for arg in node.args.args]
        returns = self._get_annotation(node.returns) if node.returns else None
        
        return FunctionInfo(
            name=node.name,
            line_number=node.lineno,
            args=args,
            returns=returns,
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )

    def _extract_import_info(self, node: ast.Import | ast.ImportFrom) -> ImportInfo:
        """Extract information from import statements"""
        if isinstance(node, ast.Import):
            return ImportInfo(
                module=node.names[0].name,
                names=[alias.name for alias in node.names],
                alias=node.names[0].asname,
                line_number=node.lineno
            )
        else:  # ImportFrom
            return ImportInfo(
                module=node.module or "",
                names=[alias.name for alias in node.names],
                line_number=node.lineno
            )

    def _is_top_level_function(self, tree: ast.Module, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if a function is at the top level (not a method)"""
        for item in tree.body:
            if item == node:
                return True
        return False

    def _calculate_complexity(self, tree: ast.Module) -> int:
        """
        Calculate cyclomatic complexity score
        Counts decision points: if, for, while, except, with, and, or
        """
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity

    def _get_name(self, node: ast.expr) -> str:
        """Get the name from an AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def _get_annotation(self, node: ast.expr) -> str:
        """Get type annotation as string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ast.unparse(node)

# Made with Bob
