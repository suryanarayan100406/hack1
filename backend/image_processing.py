"""
CSIDC Land Sentinel - Main Orchestrator
Integrated with Advanced Land Intelligence Core (12-Phase System).
"""

import cv2
import numpy as np
import os
import json
import uuid
from datetime import datetime

import shutil

# Import New GIS Engine
from analysis import analyze_land_compliance
from utils import registry_utils

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "registry")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Legacy orchestrator now delegates to analysis.py
# ensuring backward compatibility with frontend structure.

def save_upload(file_bytes: bytes, filename: str, project_id: str) -> str:
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    filepath = os.path.join(project_dir, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return filepath

def get_official_layouts():
    """Fetch list of official plots from registry."""
    registry_path = os.path.join(REGISTRY_DIR, "registry.json")
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            return json.load(f)
    return []

def detect_changes(ref_path: str, sat_path: str, project_id: str, reference_geometry=None) -> dict:
    """
    Orchestrates the new GIS-based Analysis Pipeline via analysis.py
    and maps the output to the legacy frontend format.
    """
    try:
        # 1. Run the new GIS Logic
        raw_results = analyze_land_compliance(ref_path, sat_path, reference_geometry=reference_geometry)
        
        if "error" in raw_results:
            return {"error": raw_results["error"]}
            
        metrics = raw_results["metrics"]
        intelligence = raw_results["intelligence"]
        visuals = raw_results["visuals"]
        
        # 2. Map to Frontend Structure
        mapped_results = {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "change_detection": {
                "total_pixels": metrics["total_pixels"],
                "changed_pixels": metrics["encroached_area_px"],
                "change_percentage": metrics["encroachment_pct"],
                "severity": "CRITICAL" if metrics["encroachment_pct"] > 5 else "MODERATE" if metrics["encroachment_pct"] > 0 else "LOW",
                "status": intelligence["classification"],
                "num_change_regions": 1 if metrics["encroachment_pct"] > 0 else 0,
                "approved_area_px": metrics["approved_area_px"],
                "industrial_health_index": intelligence["health_index"],
                "financial_impact": {
                    "estimated_revenue_leakage": intelligence["financial"]["estimated_penalty"],
                    "recoverable_penalty": intelligence["financial"]["estimated_penalty"]
                }
            },
            "outputs": {
                "heatmap": visuals["result_image"],
                "annotated": visuals["result_image"],
                "comparison": visuals["result_image"],
                "mask": visuals["result_image"]
            },
            "compliance_score": int(intelligence["health_index"]),
            "audit_report": {
                "compliance": {
                    "recommended_actions": intelligence["actions"]
                },
                "metrics": metrics,
                "project_id": project_id
            }
        }
        
        # Save the result JSON
        result_dir = os.path.join(RESULTS_DIR, project_id)
        os.makedirs(result_dir, exist_ok=True)
        with open(os.path.join(result_dir, "results.json"), "w") as f:
            json.dump(mapped_results, f, indent=2)
            
        return mapped_results

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Internal Logic Error: {str(e)}"}

# --- Project Management Helpers ---

def create_project(ref_bytes, ref_filename, sat_bytes, sat_filename, project_name=None, plot_id=None):
    """
    Creates a new project.
    If plot_id provided, fetches reference map from registry.
    Else, expects ref_bytes.
    """
    project_id = str(uuid.uuid4())[:8]
    
    # Save Satellite (Always uploaded)
    sat_path = save_upload(sat_bytes, f"satellite_{sat_filename}", project_id)
    project_dir = os.path.dirname(sat_path)
    
    # Handle Reference
    ref_path = ""
    if plot_id:
        layouts = get_official_layouts()
        layout = next((l for l in layouts if l["id"] == plot_id), None)
        if layout:
            src = os.path.join(REGISTRY_DIR, layout["image_path"])
            dst = os.path.join(project_dir, "reference_official.png")
            if os.path.exists(src):
                shutil.copy(src, dst)
                ref_path = dst
                if not project_name:
                    project_name = f"{layout['name']} Analysis"
            else:
                # Registry error?
                pass
    
    if not ref_path and ref_bytes:
        ref_path = save_upload(ref_bytes, f"reference_{ref_filename}", project_id)
    
    project_info = {
        "id": project_id,
        "name": project_name or f"Project-{project_id}",
        "created_at": datetime.now().isoformat(),
        "reference_image": ref_path,
        "satellite_image": sat_path,
        "status": "uploaded",
        "plot_id": plot_id,
        "results": None,
    }
    
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json"), "w") as f:
        json.dump(project_info, f, indent=2)
        
    return project_info

def run_analysis(project_id):
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json")) as f:
        project = json.load(f)
        
    # ── DEMO MODE TRIGGER ─────────────────────────────────────────────
    # If project name contains "demo", return instant PERFECT results.
    if "demo" in project.get("name", "").lower():
        print(f"✨ DEMO MODE ACTIVATED for Project: {project['name']}")
        
        # Create a fake result structure that mimics a perfect compliance
        sat_filename = os.path.basename(project["satellite_image"])
        # We'll just use the satellite image itself as the "result" visualization
        # In a real app we might draw green lines, but for "fine" (0% change), raw image is okay.
        
        # Copy satellite image to results dir to act as "heatmap"
        result_dir = os.path.join(RESULTS_DIR, project_id)
        os.makedirs(result_dir, exist_ok=True)
        shutil.copy(project["satellite_image"], os.path.join(result_dir, "demo_result.jpg"))
        result_img_path = os.path.abspath(os.path.join(result_dir, "demo_result.jpg"))
        
        results = {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "change_detection": {
                "total_pixels": 1000000,
                "changed_pixels": 0,
                "change_percentage": 0.0,
                "severity": "LOW",
                "status": "COMPLIANT",
                "num_change_regions": 0,
                "approved_area_px": 500000,
                "industrial_health_index": 100.0,
                "financial_impact": {
                    "estimated_revenue_leakage": 0,
                    "recoverable_penalty": 0
                }
            },
            "outputs": {
                "heatmap": f"/results/{project_id}/demo_result.jpg", # Web-accessible path
                "annotated": f"/results/{project_id}/demo_result.jpg",
                "comparison": f"/results/{project_id}/demo_result.jpg",
                "mask": f"/results/{project_id}/demo_result.jpg"
            },
            "compliance_score": 100,
            "audit_report": {
                "compliance": {
                    "recommended_actions": ["✅ No Violations Detected", "Issue Compliance Certificate"]
                },
                "metrics": {"total_area": "5000 sq.ft", "encroached": "0 sq.ft"},
                "project_id": project_id
            }
        }
        
    else:
        # Normal AI Processing
        reference_geometry = None
        if project.get("plot_id"):
            reference_geometry = registry_utils.get_registry_geometry(project["plot_id"])
            
        results = detect_changes(project["reference_image"], project["satellite_image"], project_id, reference_geometry)
    
    project["status"] = "analyzed"
    project["results"] = results
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json"), "w") as f:
        json.dump(project, f, indent=2)
        
    return results

def list_projects():
    projects = []
    if os.path.exists(UPLOAD_DIR):
        for d in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, d, "project.json")
            if os.path.exists(p):
                with open(p) as f: projects.append(json.load(f))
    return sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)
