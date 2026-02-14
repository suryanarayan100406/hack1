"""
API Routes for CSIDC Land Sentinel.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from image_processing import create_project, run_analysis, list_projects, get_official_layouts
from demo_data import (
    INDUSTRIAL_AREAS,
    DEMO_PLOTS,
    DEMO_ALERTS,
    get_dashboard_stats,
    get_plots_geojson,
)
from utils import registry_utils
from datetime import datetime
import demo_data

router = APIRouter(prefix="/api")


# ── Demo Data Endpoints ──────────────────────────────────────────

@router.get("/demo-data")
async def get_demo_data():
    stats = demo_data.get_dashboard_stats()
    return {
        "stats": stats,
        "plots": stats["plots"], # Use plots from stats which includes live data
        "alerts": demo_data.DEMO_ALERTS,
        "areas": stats["areas"], # Use dynamic areas from stats
        "geojson": demo_data.get_plots_geojson()
    }


@router.get("/areas")
async def get_areas():
    """Get all industrial areas."""
    return INDUSTRIAL_AREAS


@router.get("/areas/{area_id}")
async def get_area(area_id: str):
    """Get a specific industrial area with its plots."""
    area = next((a for a in INDUSTRIAL_AREAS if a["id"] == area_id), None)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    plots = [p for p in DEMO_PLOTS if p["area_id"] == area_id]
    geojson = get_plots_geojson(area_id)
    
    return {
        "area": area,
        "plots": plots,
        "geojson": geojson,
    }


@router.get("/plots")
async def get_plots(area_id: Optional[str] = None, status: Optional[str] = None):
    """Get plots with optional filtering."""
    plots = DEMO_PLOTS
    if area_id:
        plots = [p for p in plots if p["area_id"] == area_id]
    if status:
        plots = [p for p in plots if p["status"] == status]
    return plots


@router.get("/plots/{plot_id}")
async def get_plot(plot_id: str):
    """Get a specific plot."""
    plot = next((p for p in DEMO_PLOTS if p["id"] == plot_id), None)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot


@router.get("/geojson")
async def get_geojson(area_id: Optional[str] = None):
    """Get plots as GeoJSON for map display."""
    return get_plots_geojson(area_id)


@router.get("/alerts")
async def get_alerts():
    """Get all alerts."""
    return DEMO_ALERTS


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    return get_dashboard_stats()


# ── Registry Endpoints ───────────────────────────────────────────

@router.get("/official-layouts")
async def get_layouts():
    """List official layouts from registry."""
    return get_official_layouts()

@router.get("/registry")
async def get_registry():
    """Returns the list of available registry items."""
    return registry_utils.get_registry_index()

@router.get("/registry/geojson")
async def get_registry_geojson():
    """Returns the registry data as GeoJSON for map display."""
    return registry_utils.get_registry_geojson()

@router.get("/registry/thumbnails/{filename}")
async def get_registry_thumbnail(filename: str):
    """Serves the static thumbnail images."""
    file_path = os.path.join("registry", "thumbnails", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Thumbnail not found"}


# ── Image Analysis Endpoints ─────────────────────────────────────

@router.post("/upload")
async def upload_images(
    reference: Optional[UploadFile] = File(None),
    satellite: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    plot_id: Optional[str] = Form(None),
):
    """
    Upload satellite image and either reference map OR plot_id.
    """
    if not reference and not plot_id:
        raise HTTPException(status_code=400, detail="Either reference map or plot_id is required")

    ref_bytes = await reference.read() if reference else None
    ref_filename = reference.filename if reference else None
    
    sat_bytes = await satellite.read()
    
    project = create_project(
        ref_bytes, ref_filename,
        sat_bytes, satellite.filename,
        project_name,
        plot_id
    )
    
    return {
        "message": "Images uploaded successfully",
        "project": project,
    }


@router.post("/analyze/{project_id}")
async def analyze_project(project_id: str):
    """Run change detection analysis on uploaded images."""
    results = run_analysis(project_id)
    
    if "error" in results:
        raise HTTPException(status_code=404, detail=results["error"])
    
    return results


@router.get("/projects")
async def get_projects():
    """List all analysis projects."""
    return list_projects()


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project with results."""
    projects = list_projects()
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

from fastapi.responses import FileResponse
from utils.report_generator import generate_pdf_report
import os

@router.get("/reports/{project_id}/pdf")
async def get_project_pdf(project_id: str):
    """
    Generate and stream an official PDF report for the project.
    """
    # 1. Get Project Data
    projects = list_projects()
    project = next((p for p in projects if p["id"] == project_id), None)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 2. Add extra details (from registry if needed)
    # The project object usually has what we need
    
    # 3. Generate PDF
    # Save to temp or results folder
    RESULTS_DIR = "results" # Should align with image_processing.py
    project_result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(project_result_dir, exist_ok=True)
    
    pdf_path = os.path.join(project_result_dir, f"report_{project_id}.pdf")
    
    try:
        generate_pdf_report(project, pdf_path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF Generation Failed: {e}")
        
    return FileResponse(pdf_path, media_type='application/pdf', filename=f"CSIDC_Report_{project_id}.pdf")

@router.get("/mobile/alerts")
async def get_mobile_alerts():
    """
    Get simplified alerts for the Android App.
    Aggregates data from live analysis projects.
    """
    projects = list_projects()
    alerts = []
    
    for p in projects:
        # Check for violation
        results = p.get("results", {})
        change_data = results.get("change_detection", {})
        status = change_data.get("status", "UNKNOWN")
        
        if "VIOLATION" in status or "ENCROACHMENT" in status:
            pct = change_data.get("change_percentage", 0)
            alert = {
                "title": f"🚨 High Priority: {p.get('name')}",
                "plotId": p.get("id"),
                "description": f"Encroachment of {pct}% detected.",
                "severity": "HIGH"
            }
            alerts.append(alert)
            
    # Add some demo alerts if empty (so the user sees something)
    if not alerts:
        alerts = [
            {"title": "✅ System Active", "plotId": "SYS-001", "description": "No active violations detected.", "severity": "LOW"}
        ]
        
    return alerts

from pydantic import BaseModel

class VerificationRequest(BaseModel):
    plot_id: str
    officer_id: str
    status: str # VERIFIED, REJECTED, FLAGGED
    notes: str

@router.post("/mobile/verify")
async def verify_alert(request: VerificationRequest):
    """
    Handle field verification from Mobile App.
    """
    # In a real app, this would update the database.
    # For MVP, we'll log it and maybe update the demo stats in memory if possible,
    # or just return success.
    print(f"Received Verification: {request}")
    
    return {
        "status": "success",
        "message": f"Plot {request.plot_id} marked as {request.status}",
        "action_id": f"ACT-{int(datetime.now().timestamp())}"
    }
