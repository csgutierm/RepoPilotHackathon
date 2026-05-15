"""
Unit tests for Dependency Analyzer
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.repopilot.analyzers.dependency_analyzer import DependencyAnalyzer, DependencyInfo


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with sample files"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create requirements.txt
    req_file = temp_dir / "requirements.txt"
    req_file.write_text('''
fastapi>=0.115.0
pydantic>=2.9.0
pytest>=8.3.0
''')
    
    # Create pyproject.toml
    pyproject = temp_dir / "pyproject.toml"
    pyproject.write_text('''
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
]
''')
    
    # Create source directory
    src_dir = temp_dir / "src" / "myproject"
    src_dir.mkdir(parents=True)
    
    # Create a Python file with imports
    sample_file = src_dir / "main.py"
    sample_file.write_text('''
import os
import sys
from pathlib import Path
from typing import Dict, List
import fastapi
from myproject.utils import helper
''')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestDependencyAnalyzer:
    """Test suite for DependencyAnalyzer"""
    
    def test_analyzer_initialization(self, temp_project_dir):
        """Test analyzer can be initialized"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        assert analyzer is not None
        assert analyzer.project_root == temp_project_dir
        assert len(analyzer.dependencies) == 0
    
    def test_parse_requirements(self, temp_project_dir):
        """Test parsing requirements.txt"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer._analyze_requirements()
        
        assert "fastapi" in analyzer.dependencies
        assert "pydantic" in analyzer.dependencies
        assert "pytest" in analyzer.dependencies
    
    def test_parse_pyproject(self, temp_project_dir):
        """Test parsing pyproject.toml"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer._analyze_pyproject()
        
        assert "fastapi" in analyzer.dependencies or "uvicorn" in analyzer.dependencies
    
    def test_analyze_imports(self, temp_project_dir):
        """Test analyzing imports from Python files"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer._analyze_imports()
        
        # Should detect standard library imports
        assert "os" in analyzer.dependencies or "sys" in analyzer.dependencies
    
    def test_standard_library_detection(self, temp_project_dir):
        """Test detecting standard library modules"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.analyze_project()
        
        # Check that standard library modules are marked correctly
        if "os" in analyzer.dependencies:
            assert analyzer.dependencies["os"].is_standard_lib is True
    
    def test_dependency_report(self, temp_project_dir):
        """Test generating dependency report"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        report = analyzer.analyze_project()
        
        assert "total_dependencies" in report
        assert "external_packages" in report
        assert "standard_library" in report
        assert "external_packages_list" in report
        assert isinstance(report["total_dependencies"], int)
    
    def test_dependency_graph_generation(self, temp_project_dir):
        """Test generating dependency graph"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.analyze_project()
        
        assert isinstance(analyzer.dependency_graph, dict)
    
    def test_dependency_graph_dot_format(self, temp_project_dir):
        """Test generating DOT format graph"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.analyze_project()
        
        dot_graph = analyzer.get_dependency_graph_dot()
        
        assert "digraph Dependencies" in dot_graph
        assert "rankdir=LR" in dot_graph
    
    def test_local_module_detection(self, temp_project_dir):
        """Test detecting local modules"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        
        # myproject should be detected as local
        is_local = analyzer._is_local_module("myproject.utils")
        assert is_local is True
        
        # fastapi should not be local
        is_local = analyzer._is_local_module("fastapi")
        assert is_local is False
    
    def test_empty_project(self):
        """Test analyzing an empty project"""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            analyzer = DependencyAnalyzer(temp_dir)
            report = analyzer.analyze_project()
            
            assert report["total_dependencies"] == 0
        finally:
            shutil.rmtree(temp_dir)
    
    def test_module_dependencies_tracking(self, temp_project_dir):
        """Test tracking module dependencies"""
        analyzer = DependencyAnalyzer(temp_project_dir)
        analyzer.analyze_project()
        
        assert len(analyzer.module_dependencies) > 0
        
        # Check that module dependencies have correct structure
        for dep in analyzer.module_dependencies:
            assert hasattr(dep, 'source_module')
            assert hasattr(dep, 'target_module')
            assert hasattr(dep, 'import_type')

# Made with Bob
