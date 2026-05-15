"""
Visualization API Routes - Redirect endpoints for dashboard access
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["visualization"])

# Store analysis results (in production, use a database)
_analysis_store = {}
_latest_analysis_id = None


def store_analysis(analysis_id: str, data: dict) -> None:
    """Store analysis results"""
    global _latest_analysis_id
    _analysis_store[analysis_id] = {
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    _latest_analysis_id = analysis_id


def get_analysis(analysis_id: str) -> Optional[dict]:
    """Retrieve analysis results"""
    return _analysis_store.get(analysis_id)


def get_redirect_html(analysis_id: str, title: str = "RepoPilot Visualization") -> str:
    """
    Generate beautiful HTML redirect page with loading animation
    
    Args:
        analysis_id: Analysis ID to redirect to
        title: Page title
        
    Returns:
        HTML content as string
    """
    dashboard_url = f"http://localhost:8501?analysis_id={analysis_id}"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2;url={dashboard_url}">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}
        
        .container {{
            text-align: center;
            padding: 2rem;
            max-width: 600px;
        }}
        
        .logo {{
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: float 3s ease-in-out infinite;
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }}
        
        p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        .loader {{
            width: 60px;
            height: 60px;
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            margin: 2rem auto;
            animation: spin 1s linear infinite;
        }}
        
        .analysis-id {{
            background: rgba(255, 255, 255, 0.2);
            padding: 1rem;
            border-radius: 10px;
            margin-top: 2rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            word-break: break-all;
        }}
        
        .redirect-info {{
            margin-top: 2rem;
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .redirect-info a {{
            color: white;
            text-decoration: underline;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }}
        
        .feature {{
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .feature-icon {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .feature-text {{
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>{title}</h1>
        <p>Redirecting to interactive dashboard...</p>
        
        <div class="loader"></div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-text">Overview</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🏗️</div>
                <div class="feature-text">Architecture</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🔗</div>
                <div class="feature-text">Dependencies</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📚</div>
                <div class="feature-text">Documentation</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🧪</div>
                <div class="feature-text">Testing</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🎓</div>
                <div class="feature-text">Onboarding</div>
            </div>
        </div>
        
        <div class="analysis-id">
            <strong>Analysis ID:</strong><br>
            {analysis_id}
        </div>
        
        <div class="redirect-info">
            If you are not redirected automatically,
            <a href="{dashboard_url}">click here</a>.
        </div>
    </div>
    
    <script>
        // Smooth redirect after animation
        setTimeout(() => {{
            window.location.href = '{dashboard_url}';
        }}, 2000);
    </script>
</body>
</html>
    """
    
    return html_content


@router.get("/visualize", response_class=HTMLResponse)
async def visualize_latest() -> HTMLResponse:
    """
    Redirect to the latest analysis visualization
    
    Returns:
        HTML redirect page
    """
    if not _latest_analysis_id:
        raise HTTPException(
            status_code=404,
            detail="No analysis available. Please run an analysis first."
        )
    
    html = get_redirect_html(
        _latest_analysis_id,
        "RepoPilot - Latest Analysis"
    )
    
    return HTMLResponse(content=html)


@router.get("/visualize/{analysis_id}", response_class=HTMLResponse)
async def visualize_analysis(analysis_id: str) -> HTMLResponse:
    """
    Redirect to a specific analysis visualization
    
    Args:
        analysis_id: The analysis ID to visualize
        
    Returns:
        HTML redirect page
    """
    analysis = get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found: {analysis_id}"
        )
    
    html = get_redirect_html(
        analysis_id,
        f"RepoPilot - Analysis {analysis_id[:8]}"
    )
    
    return HTMLResponse(content=html)


@router.get("/visualize/{analysis_id}/data")
async def get_visualization_data(analysis_id: str) -> dict:
    """
    Get the raw data for a specific analysis
    
    Args:
        analysis_id: The analysis ID
        
    Returns:
        Analysis data
    """
    analysis = get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found: {analysis_id}"
        )
    
    return {
        "analysis_id": analysis_id,
        "timestamp": analysis['timestamp'],
        "data": analysis['data']
    }


@router.get("/visualize/list")
async def list_analyses() -> dict:
    """
    List all available analyses
    
    Returns:
        List of analysis IDs and timestamps
    """
    analyses = []
    for analysis_id, data in _analysis_store.items():
        analyses.append({
            "analysis_id": analysis_id,
            "timestamp": data['timestamp'],
            "is_latest": analysis_id == _latest_analysis_id
        })
    
    # Sort by timestamp, newest first
    analyses.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return {
        "total": len(analyses),
        "latest_id": _latest_analysis_id,
        "analyses": analyses
    }


@router.delete("/visualize/{analysis_id}")
async def delete_analysis(analysis_id: str) -> dict:
    """
    Delete a specific analysis
    
    Args:
        analysis_id: The analysis ID to delete
        
    Returns:
        Success message
    """
    global _latest_analysis_id
    
    if analysis_id not in _analysis_store:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis not found: {analysis_id}"
        )
    
    del _analysis_store[analysis_id]
    
    # Update latest if we deleted it
    if _latest_analysis_id == analysis_id:
        _latest_analysis_id = list(_analysis_store.keys())[-1] if _analysis_store else None
    
    return {
        "message": f"Analysis {analysis_id} deleted successfully",
        "remaining": len(_analysis_store)
    }

# Made with Bob
