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

router = APIRouter(prefix="/api")


# ── Demo Data Endpoints ──────────────────────────────────────────

@router.get("/demo-data")
async def get_demo_data():
    """Get all demo data for the dashboard."""
    return {
        "areas": INDUSTRIAL_AREAS,
        "plots": DEMO_PLOTS,
        "alerts": DEMO_ALERTS,
        "stats": get_dashboard_stats(),
        "geojson": get_plots_geojson(),
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
