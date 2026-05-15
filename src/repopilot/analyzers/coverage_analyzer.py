"""
Coverage Analyzer - Analyzes test coverage and provides recommendations
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TestInfo:
    """Information about a test"""
    name: str
    file_path: str
    line_number: int
    test_type: str  # 'unit', 'integration', 'functional'
    tested_module: Optional[str] = None


@dataclass
class ModuleCoverage:
    """Coverage information for a module"""
    module_path: str
    total_functions: int
    tested_functions: Set[str] = field(default_factory=set)
    total_classes: int = 0
    tested_classes: Set[str] = field(default_factory=set)
    coverage_percentage: float = 0.0
    missing_tests: List[str] = field(default_factory=list)


class CoverageAnalyzer:
    """
    Analyzes test coverage and provides recommendations:
    - Identifies tested vs untested code
    - Calculates coverage percentages
    - Suggests missing tests
    - Identifies critical paths without tests
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.tests: List[TestInfo] = []
        self.module_coverage: Dict[str, ModuleCoverage] = {}
        self.src_path = project_root / "src"
        self.test_path = project_root / "tests"

    def analyze_coverage(self) -> Dict[str, Any]:
        """
        Perform complete coverage analysis
        
        Returns:
            Dictionary with coverage metrics and recommendations
        """
        # Analyze test files
        self._analyze_test_files()
        
        # Analyze source files
        self._analyze_source_files()
        
        # Match tests to source code
        self._match_tests_to_source()
        
        # Calculate coverage
        self._calculate_coverage()
        
        return self.get_coverage_report()

    def _analyze_test_files(self) -> None:
        """Analyze all test files to identify tests"""
        if not self.test_path.exists():
            return
        
        test_files = list(self.test_path.rglob("test_*.py"))
        
        for test_file in test_files:
            try:
                self._extract_tests_from_file(test_file)
            except Exception as e:
                print(f"Warning: Could not analyze test file {test_file}: {str(e)}")

    def _extract_tests_from_file(self, file_path: Path) -> None:
        """Extract test functions and classes from a test file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            relative_path = str(file_path.relative_to(self.project_root))
            
            # Determine test type from path
            test_type = self._determine_test_type(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        # Extract tested module from test name or imports
                        tested_module = self._infer_tested_module(node, tree, file_path)
                        
                        self.tests.append(TestInfo(
                            name=node.name,
                            file_path=relative_path,
                            line_number=node.lineno,
                            test_type=test_type,
                            tested_module=tested_module
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        # Extract test methods from test class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                                tested_module = self._infer_tested_module(item, tree, file_path)
                                
                                self.tests.append(TestInfo(
                                    name=f"{node.name}.{item.name}",
                                    file_path=relative_path,
                                    line_number=item.lineno,
                                    test_type=test_type,
                                    tested_module=tested_module
                                ))
        
        except Exception as e:
            raise ValueError(f"Error extracting tests from {file_path}: {str(e)}")

    def _determine_test_type(self, file_path: Path) -> str:
        """Determine test type based on file location"""
        path_str = str(file_path)
        if 'unit' in path_str:
            return 'unit'
        elif 'integration' in path_str:
            return 'integration'
        elif 'functional' in path_str or 'e2e' in path_str:
            return 'functional'
        return 'unit'  # Default

    def _infer_tested_module(self, node: ast.FunctionDef, tree: ast.Module, file_path: Path) -> Optional[str]:
        """Infer which module is being tested"""
        # Try to extract from imports
        for item in tree.body:
            if isinstance(item, ast.ImportFrom):
                if item.module and 'repopilot' in item.module:
                    return item.module
        
        # Try to infer from test file name
        # e.g., test_ast_analyzer.py -> repopilot.analyzers.ast_analyzer
        file_name = file_path.stem
        if file_name.startswith('test_'):
            module_name = file_name[5:]  # Remove 'test_' prefix
            
            # Try to find corresponding source file
            if 'unit' in str(file_path):
                # Look in src directory
                possible_paths = list(self.src_path.rglob(f"{module_name}.py"))
                if possible_paths:
                    rel_path = possible_paths[0].relative_to(self.src_path)
                    return str(rel_path).replace('\\', '.').replace('/', '.').replace('.py', '')
        
        return None

    def _analyze_source_files(self) -> None:
        """Analyze source files to identify functions and classes"""
        if not self.src_path.exists():
            return
        
        source_files = list(self.src_path.rglob("*.py"))
        
        for source_file in source_files:
            if source_file.name == '__init__.py':
                continue
            
            try:
                self._analyze_source_file(source_file)
            except Exception as e:
                print(f"Warning: Could not analyze source file {source_file}: {str(e)}")

    def _analyze_source_file(self, file_path: Path) -> None:
        """Analyze a single source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            relative_path = str(file_path.relative_to(self.src_path))
            module_name = relative_path.replace('\\', '.').replace('/', '.').replace('.py', '')
            
            functions = []
            classes = []
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Public functions
                        functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            self.module_coverage[module_name] = ModuleCoverage(
                module_path=relative_path,
                total_functions=len(functions),
                total_classes=len(classes)
            )
            
        except Exception as e:
            raise ValueError(f"Error analyzing source file {file_path}: {str(e)}")

    def _match_tests_to_source(self) -> None:
        """Match tests to their corresponding source modules"""
        for test in self.tests:
            if test.tested_module and test.tested_module in self.module_coverage:
                # Extract function/class name from test name
                # e.g., test_analyze_file -> analyze_file
                test_name = test.name.split('.')[-1]  # Get last part if it's a class method
                if test_name.startswith('test_'):
                    tested_item = test_name[5:]  # Remove 'test_' prefix
                    
                    # Mark as tested (simplified - in production, use more sophisticated matching)
                    self.module_coverage[test.tested_module].tested_functions.add(tested_item)

    def _calculate_coverage(self) -> None:
        """Calculate coverage percentages for each module"""
        for module_name, coverage in self.module_coverage.items():
            total_items = coverage.total_functions + coverage.total_classes
            tested_items = len(coverage.tested_functions) + len(coverage.tested_classes)
            
            if total_items > 0:
                coverage.coverage_percentage = (tested_items / total_items) * 100
            else:
                coverage.coverage_percentage = 100.0  # Empty modules are "fully covered"

    def get_coverage_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive coverage report
        
        Returns:
            Dictionary with coverage metrics and recommendations
        """
        total_modules = len(self.module_coverage)
        total_tests = len(self.tests)
        
        # Calculate overall coverage
        if total_modules > 0:
            overall_coverage = sum(
                c.coverage_percentage for c in self.module_coverage.values()
            ) / total_modules
        else:
            overall_coverage = 0.0
        
        # Identify modules with low coverage
        low_coverage_modules = [
            {
                "module": name,
                "coverage": round(cov.coverage_percentage, 2),
                "total_functions": cov.total_functions,
                "tested_functions": len(cov.tested_functions)
            }
            for name, cov in self.module_coverage.items()
            if cov.coverage_percentage < 80
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return {
            "overall_coverage": round(overall_coverage, 2),
            "total_tests": total_tests,
            "total_modules": total_modules,
            "test_breakdown": {
                "unit": len([t for t in self.tests if t.test_type == 'unit']),
                "integration": len([t for t in self.tests if t.test_type == 'integration']),
                "functional": len([t for t in self.tests if t.test_type == 'functional'])
            },
            "module_coverage": [
                {
                    "module": name,
                    "coverage": round(cov.coverage_percentage, 2),
                    "total_functions": cov.total_functions,
                    "tested_functions": len(cov.tested_functions),
                    "total_classes": cov.total_classes
                }
                for name, cov in self.module_coverage.items()
            ],
            "low_coverage_modules": low_coverage_modules,
            "recommendations": recommendations
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate test coverage recommendations"""
        recommendations = []
        
        # Check for modules without tests
        untested_modules = [
            name for name, cov in self.module_coverage.items()
            if cov.coverage_percentage == 0
        ]
        
        if untested_modules:
            recommendations.append(
                f"Add tests for {len(untested_modules)} untested modules: {', '.join(untested_modules[:3])}"
            )
        
        # Check for low coverage modules
        low_coverage = [
            name for name, cov in self.module_coverage.items()
            if 0 < cov.coverage_percentage < 50
        ]
        
        if low_coverage:
            recommendations.append(
                f"Improve coverage for {len(low_coverage)} modules with <50% coverage"
            )
        
        # Check test distribution
        unit_tests = len([t for t in self.tests if t.test_type == 'unit'])
        integration_tests = len([t for t in self.tests if t.test_type == 'integration'])
        
        if unit_tests == 0:
            recommendations.append("Add unit tests for individual components")
        
        if integration_tests == 0 and len(self.module_coverage) > 1:
            recommendations.append("Add integration tests to verify component interactions")
        
        if not recommendations:
            recommendations.append("Test coverage is good! Consider adding edge case tests.")
        
        return recommendations

# Made with Bob
