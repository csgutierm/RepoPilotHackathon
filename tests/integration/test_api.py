"""
Integration tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil

from src.repopilot.api.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create a simple Python project structure
    src_dir = temp_dir / "src" / "testproject"
    src_dir.mkdir(parents=True)
    
    # Create a sample module
    (src_dir / "__init__.py").write_text("")
    (src_dir / "main.py").write_text('''
"""Main module"""

class TestClass:
    """A test class"""
    
    def method(self):
        """A method"""
        pass

def test_function():
    """A function"""
    return True
''')
    
    # Create requirements.txt
    (temp_dir / "requirements.txt").write_text("fastapi>=0.115.0\n")
    
    # Create tests directory
    tests_dir = temp_dir / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_main.py").write_text('''
def test_example():
    assert True
''')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_api_info(self, client):
        """Test API info endpoint"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "analysis" in data["endpoints"]
        assert "generation" in data["endpoints"]
    
    def test_analyze_repository(self, client, temp_repo):
        """Test complete repository analysis"""
        response = client.post(
            "/analyze",
            json={"repository_path": str(temp_repo)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "architecture_summary" in data
        assert "dependency_report" in data
        assert "coverage_report" in data
    
    def test_analyze_architecture_only(self, client, temp_repo):
        """Test architecture analysis endpoint"""
        response = client.post(
            "/analyze/architecture",
            json={"repository_path": str(temp_repo)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "total_files" in data["data"]
    
    def test_analyze_dependencies_only(self, client, temp_repo):
        """Test dependency analysis endpoint"""
        response = client.post(
            "/analyze/dependencies",
            json={"repository_path": str(temp_repo)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "total_dependencies" in data["data"]
    
    def test_analyze_coverage_only(self, client, temp_repo):
        """Test coverage analysis endpoint"""
        response = client.post(
            "/analyze/coverage",
            json={"repository_path": str(temp_repo)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "overall_coverage" in data["data"]
    
    def test_generate_documentation(self, client, temp_repo):
        """Test documentation generation endpoint"""
        response = client.post(
            "/generate/documentation",
            json={
                "repository_path": str(temp_repo),
                "include_api_docs": True,
                "include_architecture": True,
                "include_dependencies": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "generated_files" in data
        assert len(data["generated_files"]) > 0
    
    def test_generate_onboarding(self, client, temp_repo):
        """Test onboarding report generation endpoint"""
        response = client.post(
            "/generate/onboarding",
            json={"repository_path": str(temp_repo)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "report_path" in data
    
    def test_invalid_repository_path(self, client):
        """Test handling of invalid repository path"""
        response = client.post(
            "/analyze",
            json={"repository_path": "/nonexistent/path"}
        )
        assert response.status_code == 404
    
    def test_analyze_file_instead_of_directory(self, client, temp_repo):
        """Test handling when path is a file instead of directory"""
        file_path = temp_repo / "requirements.txt"
        response = client.post(
            "/analyze",
            json={"repository_path": str(file_path)}
        )
        assert response.status_code == 400
    
    def test_missing_request_body(self, client):
        """Test handling of missing request body"""
        response = client.post("/analyze")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

# Made with Bob
