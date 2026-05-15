"""
Unit tests for AST Analyzer
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.repopilot.analyzers.ast_analyzer import ASTAnalyzer, FileAnalysis, ClassInfo, FunctionInfo


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with sample Python files"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create a sample Python file
    sample_file = temp_dir / "sample.py"
    sample_file.write_text('''
"""Sample module for testing"""

class SampleClass:
    """A sample class"""
    
    def __init__(self):
        self.value = 0
    
    def method_one(self, x: int) -> int:
        """Sample method"""
        return x + 1

def sample_function(a: int, b: int) -> int:
    """Sample function"""
    return a + b

async def async_function():
    """Async sample function"""
    pass
''')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestASTAnalyzer:
    """Test suite for ASTAnalyzer"""
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized"""
        analyzer = ASTAnalyzer()
        assert analyzer is not None
        assert analyzer.analyses == {}
    
    def test_analyze_file(self, temp_project_dir):
        """Test analyzing a single file"""
        analyzer = ASTAnalyzer()
        sample_file = temp_project_dir / "sample.py"
        
        analysis = analyzer.analyze_file(sample_file)
        
        assert isinstance(analysis, FileAnalysis)
        assert analysis.file_path == str(sample_file)
        assert analysis.docstring == "Sample module for testing"
        assert len(analysis.classes) == 1
        assert len(analysis.functions) == 2  # sample_function and async_function
    
    def test_extract_class_info(self, temp_project_dir):
        """Test extracting class information"""
        analyzer = ASTAnalyzer()
        sample_file = temp_project_dir / "sample.py"
        
        analysis = analyzer.analyze_file(sample_file)
        
        assert len(analysis.classes) == 1
        cls = analysis.classes[0]
        assert cls.name == "SampleClass"
        assert cls.docstring == "A sample class"
        assert "__init__" in cls.methods
        assert "method_one" in cls.methods
    
    def test_extract_function_info(self, temp_project_dir):
        """Test extracting function information"""
        analyzer = ASTAnalyzer()
        sample_file = temp_project_dir / "sample.py"
        
        analysis = analyzer.analyze_file(sample_file)
        
        assert len(analysis.functions) >= 1
        func = next(f for f in analysis.functions if f.name == "sample_function")
        assert func.name == "sample_function"
        assert "a" in func.args
        assert "b" in func.args
        assert func.docstring == "Sample function"
    
    def test_async_function_detection(self, temp_project_dir):
        """Test detecting async functions"""
        analyzer = ASTAnalyzer()
        sample_file = temp_project_dir / "sample.py"
        
        analysis = analyzer.analyze_file(sample_file)
        
        async_func = next(f for f in analysis.functions if f.name == "async_function")
        assert async_func.is_async is True
    
    def test_analyze_directory(self, temp_project_dir):
        """Test analyzing a directory"""
        analyzer = ASTAnalyzer()
        
        # Create another file
        another_file = temp_project_dir / "another.py"
        another_file.write_text('def another_func(): pass')
        
        analyses = analyzer.analyze_directory(temp_project_dir)
        
        assert len(analyses) >= 2
        assert str(temp_project_dir / "sample.py") in analyses
        assert str(temp_project_dir / "another.py") in analyses
    
    def test_architecture_summary(self, temp_project_dir):
        """Test generating architecture summary"""
        analyzer = ASTAnalyzer()
        sample_file = temp_project_dir / "sample.py"
        analyzer.analyze_file(sample_file)
        
        summary = analyzer.get_architecture_summary()
        
        assert "total_files" in summary
        assert "total_classes" in summary
        assert "total_functions" in summary
        assert "total_lines_of_code" in summary
        assert summary["total_files"] == 1
        assert summary["total_classes"] == 1
        assert summary["total_functions"] == 2
    
    def test_complexity_calculation(self, temp_project_dir):
        """Test complexity score calculation"""
        analyzer = ASTAnalyzer()
        
        # Create a file with complex logic
        complex_file = temp_project_dir / "complex.py"
        complex_file.write_text('''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                while i > 0:
                    i -= 1
    return x
''')
        
        analysis = analyzer.analyze_file(complex_file)
        
        assert analysis.complexity_score > 1
    
    def test_invalid_file_handling(self):
        """Test handling of invalid files"""
        analyzer = ASTAnalyzer()
        
        with pytest.raises(ValueError):
            analyzer.analyze_file(Path("nonexistent.py"))
    
    def test_imports_extraction(self, temp_project_dir):
        """Test extracting import statements"""
        analyzer = ASTAnalyzer()
        
        import_file = temp_project_dir / "imports.py"
        import_file.write_text('''
import os
from pathlib import Path
from typing import Dict, List
''')
        
        analysis = analyzer.analyze_file(import_file)
        
        assert len(analysis.imports) >= 3
        import_names = [imp.module for imp in analysis.imports]
        assert "os" in import_names
        assert "pathlib" in import_names

# Made with Bob
