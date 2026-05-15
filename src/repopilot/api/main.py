"""
FastAPI Application - Main API endpoints for RepoPilot
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import shutil
import uuid

from ..analyzers.ast_analyzer import ASTAnalyzer
from ..analyzers.dependency_analyzer import DependencyAnalyzer
from ..analyzers.coverage_analyzer import CoverageAnalyzer
from ..generators.doc_generator import DocGenerator
from ..generators.onboarding_generator import OnboardingGenerator
from .routes import visualization_router
from .routes.visualization import store_analysis


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    """Request model for repository analysis"""
    repository_path: str = Field(..., description="Path to the repository to analyze")


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    status: str
    architecture_summary: Dict[str, Any]
    dependency_report: Dict[str, Any]
    coverage_report: Dict[str, Any]
    message: str


class DocumentationRequest(BaseModel):
    """Request model for documentation generation"""
    repository_path: str
    include_api_docs: bool = True
    include_architecture: bool = True
    include_dependencies: bool = True


class OnboardingRequest(BaseModel):
    """Request model for onboarding report generation"""
    repository_path: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


# Create FastAPI app
app = FastAPI(
    title="RepoPilot API",
    description="Python Repository Analysis Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(visualization_router)


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Root endpoint - API information
    """
    return {
        "name": "RepoPilot API",
        "version": "0.1.0",
        "description": "Python Repository Analysis Platform",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze a Python repository
    
    Performs comprehensive analysis including:
    - AST-based code analysis
    - Dependency analysis
    - Test coverage analysis
    
    Args:
        request: Analysis request with repository path
        
    Returns:
        Complete analysis results
    """
    try:
        repo_path = Path(request.repository_path)
        
        if not repo_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Repository path not found: {request.repository_path}"
            )
        
        if not repo_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {request.repository_path}"
            )
        
        # Perform AST analysis
        ast_analyzer = ASTAnalyzer()
        ast_analyzer.analyze_directory(repo_path)
        architecture_summary = ast_analyzer.get_architecture_summary()
        
        # Perform dependency analysis
        dep_analyzer = DependencyAnalyzer(repo_path)
        dependency_report = dep_analyzer.analyze_project()
        
        # Perform coverage analysis
        coverage_analyzer = CoverageAnalyzer(repo_path)
        coverage_report = coverage_analyzer.analyze_coverage()
        
        # Store analysis for visualization
        analysis_id = str(uuid.uuid4())
        store_analysis(analysis_id, {
            'architecture': architecture_summary,
            'dependencies': dependency_report,
            'coverage': coverage_report,
            'ast_analyses': ast_analyzer.analyses
        })
        
        response = AnalysisResponse(
            status="success",
            architecture_summary=architecture_summary,
            dependency_report=dependency_report,
            coverage_report=coverage_report,
            message=f"Analysis completed successfully. View at /api/v1/visualize/{analysis_id}"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/architecture")
async def analyze_architecture(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze repository architecture only
    
    Args:
        request: Analysis request with repository path
        
    Returns:
        Architecture summary
    """
    try:
        repo_path = Path(request.repository_path)
        
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository path not found")
        
        ast_analyzer = ASTAnalyzer()
        ast_analyzer.analyze_directory(repo_path)
        architecture_summary = ast_analyzer.get_architecture_summary()
        
        return {
            "status": "success",
            "data": architecture_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/dependencies")
async def analyze_dependencies(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze repository dependencies only
    
    Args:
        request: Analysis request with repository path
        
    Returns:
        Dependency report
    """
    try:
        repo_path = Path(request.repository_path)
        
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository path not found")
        
        dep_analyzer = DependencyAnalyzer(repo_path)
        dependency_report = dep_analyzer.analyze_project()
        
        return {
            "status": "success",
            "data": dependency_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/coverage")
async def analyze_coverage(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze test coverage only
    
    Args:
        request: Analysis request with repository path
        
    Returns:
        Coverage report
    """
    try:
        repo_path = Path(request.repository_path)
        
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository path not found")
        
        coverage_analyzer = CoverageAnalyzer(repo_path)
        coverage_report = coverage_analyzer.analyze_coverage()
        
        return {
            "status": "success",
            "data": coverage_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/documentation")
async def generate_documentation(request: DocumentationRequest) -> Dict[str, Any]:
    """
    Generate documentation for a repository
    
    Args:
        request: Documentation generation request
        
    Returns:
        Paths to generated documentation files
    """
    try:
        repo_path = Path(request.repository_path)
        
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository path not found")
        
        doc_generator = DocGenerator(repo_path)
        generated_files = []
        
        # Generate architecture documentation
        if request.include_architecture:
            ast_analyzer = ASTAnalyzer()
            ast_analyzer.analyze_directory(repo_path)
            architecture_summary = ast_analyzer.get_architecture_summary()
            
            arch_doc = doc_generator.generate_architecture_docs(architecture_summary)
            arch_path = doc_generator.save_documentation("ARCHITECTURE.md", arch_doc)
            generated_files.append(str(arch_path))
        
        # Generate dependency documentation
        if request.include_dependencies:
            dep_analyzer = DependencyAnalyzer(repo_path)
            dependency_report = dep_analyzer.analyze_project()
            
            dep_doc = doc_generator.generate_dependency_docs(dependency_report)
            dep_path = doc_generator.save_documentation("DEPENDENCIES.md", dep_doc)
            generated_files.append(str(dep_path))
        
        return {
            "status": "success",
            "generated_files": generated_files,
            "message": "Documentation generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/onboarding")
async def generate_onboarding(request: OnboardingRequest) -> Dict[str, Any]:
    """
    Generate onboarding report for a repository
    
    Args:
        request: Onboarding generation request
        
    Returns:
        Path to generated onboarding report
    """
    try:
        repo_path = Path(request.repository_path)
        
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository path not found")
        
        # Perform all analyses
        ast_analyzer = ASTAnalyzer()
        ast_analyzer.analyze_directory(repo_path)
        architecture_summary = ast_analyzer.get_architecture_summary()
        
        dep_analyzer = DependencyAnalyzer(repo_path)
        dependency_report = dep_analyzer.analyze_project()
        
        coverage_analyzer = CoverageAnalyzer(repo_path)
        coverage_report = coverage_analyzer.analyze_coverage()
        
        # Generate onboarding report
        onboarding_gen = OnboardingGenerator(repo_path)
        report = onboarding_gen.generate_onboarding_report(
            architecture_summary,
            dependency_report,
            coverage_report,
            ast_analyzer.analyses
        )
        
        report_path = onboarding_gen.save_onboarding_report(report)
        
        return {
            "status": "success",
            "report_path": str(report_path),
            "message": "Onboarding report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info")
async def get_api_info() -> Dict[str, Any]:
    """
    Get API information and available endpoints
    """
    return {
        "name": "RepoPilot API",
        "version": "0.1.0",
        "endpoints": {
            "analysis": {
                "POST /analyze": "Complete repository analysis",
                "POST /analyze/architecture": "Architecture analysis only",
                "POST /analyze/dependencies": "Dependency analysis only",
                "POST /analyze/coverage": "Coverage analysis only"
            },
            "generation": {
                "POST /generate/documentation": "Generate documentation",
                "POST /generate/onboarding": "Generate onboarding report"
            },
            "utility": {
                "GET /": "API root",
                "GET /health": "Health check",
                "GET /info": "API information"
            }
        }
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
