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

# Import New Core Engines
# Import New Core Engines
from core.intelligence import IntelligenceEngine
from core.compliance import ComplianceEngine
from core.economics import EconomicsEngine
from core.reporting import ReportingEngine

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Initialize Engines
intelligence = IntelligenceEngine()
compliance = ComplianceEngine()
economics = EconomicsEngine()
reporting = ReportingEngine(RESULTS_DIR)

def save_upload(file_bytes: bytes, filename: str, project_id: str) -> str:
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    filepath = os.path.join(project_dir, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return filepath

def detect_changes(ref_path: str, sat_path: str, project_id: str) -> dict:
    """
    Orchestrates the 12-Phase Advanced Analysis Pipeline.
    """
    # Load Images
    ref_img = cv2.imread(ref_path)
    sat_img = cv2.imread(sat_path)
    
    if ref_img is None or sat_img is None:
        return {"error": "Could not load images"}
        
    # --- PRE-PROCESSING ---
    # Align Satellite to Map (Simple Resize for MVP compatibility)
    h, w = ref_img.shape[:2]
    sat_aligned = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    
    # --- PHASE 1: RASTER-TO-VECTOR RECONSTRUCTION ---
    # Extract plots from reference map
    plots = intelligence.extract_plot_polygons(ref_img)
    
    # If no valid plots found, fallback to whole image as one plot (Legacy mode logic)
    if not plots:
        plots = [{
            "id": "PLOT-DEFAULT",
            "polygon_points": np.array([[0,0], [w,0], [w,h], [0,h]]),
            "pixel_area": w*h,
            "centroid": (w//2, h//2),
            "bbox": (0, 0, w, h)
        }]
        
    # --- PHASE 2: OCR IDENTIFICATION ---
    plots = intelligence.identify_plot_ids(ref_img, plots)
    
    # --- PHASE 3: GEOREFERENCING ---
    # Mock map bounds for demo. In real app, these come from user input or metadata
    map_bounds = { "min_lat": 21.25, "max_lat": 21.26, "min_lon": 81.62, "max_lon": 81.63, "width_px": w, "height_px": h }
    plots = intelligence.georeference_plots(plots, map_bounds)
    
    # Process the MAIN plot (Largest) for single-plot analysis compatibility
    # The frontend expects a single result for now, so we focus on the primary plot.
    # In a full multi-plot system, we'd loop through all.
    primary_plot = max(plots, key=lambda p: p["pixel_area"])
    
    # --- PHASE 4: SATELLITE ANALYSIS ---
    sat_analysis = intelligence.analyze_satellite_builtup(sat_aligned, primary_plot["polygon_points"])
    
    # --- PHASE 5: TRUE ENCROACHMENT ---
    # Create mask for primary plot
    plot_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(plot_mask, [np.array(primary_plot["polygon_points"])], 255)
    
    # Built-up mask needs to be full size for compliance engine
    built_up_full = np.zeros((h, w), dtype=np.uint8)
    if sat_analysis["built_up_mask"] is not None:
        bx, by, bw, bh = primary_plot["bbox"]
        # Place crop back (handle sizing safety)
        sh, sw = sat_analysis["built_up_mask"].shape
        built_up_full[by:by+sh, bx:bx+sw] = sat_analysis["built_up_mask"]
        
    compliance_metrics = compliance.compute_encroachment(plot_mask, built_up_full)
    
    # --- PHASE 6: CLASSIFICATION ---
    classification = compliance.classify_land(compliance_metrics)
    
    # --- PHASE 7: RISK SCORING ---
    risk_score = compliance.calculate_risk_score(compliance_metrics["encroachment_pct"])
    
    # --- PHASE 8: FINANCIAL IMPACT ---
    # Assume 1 pixel ~ 10 sqft for demo scale (or calculate from georef)
    plot_area_sqft = compliance_metrics["approved_px"] * 0.1 
    financials = economics.estimate_financial_impact(plot_area_sqft, compliance_metrics, classification)
    
    # --- PHASE 9: INDUSTRIAL HEALTH INDEX ---
    health_index = economics.calculate_health_index(compliance_metrics, risk_score["score"])
    
    # --- PHASE 11: DECISION ENGINE ---
    actions = compliance.recommend_actions(risk_score, classification)
    
    # --- PHASE 12: VISUALIZATION & REPORTING ---
    # Generate Overlay
    overlay, _ = generate_legacy_overlay(sat_aligned, plot_mask, compliance_metrics["masks"]["encroachment"])
    
    result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_dir, exist_ok=True)
    
    cv2.imwrite(os.path.join(result_dir, "heatmap.png"), overlay)
    cv2.imwrite(os.path.join(result_dir, "annotated.png"), overlay)
    cv2.imwrite(os.path.join(result_dir, "comparison.png"), np.hstack([ref_img, sat_aligned]))
    cv2.imwrite(os.path.join(result_dir, "mask.png"), compliance_metrics["masks"]["encroachment"])
    
    # Generate Audit JSON
    audit_data = {
        "plot_id": primary_plot.get("plot_id"),
        "coordinates": primary_plot.get("coordinates"),
        "area_sqft": plot_area_sqft
    }
    comp_data = {
        "classification": classification,
        "risk": risk_score,
        "encroachment_pct": compliance_metrics["encroachment_pct"],
        "utilization_pct": compliance_metrics["utilization_pct"],
        "actions": actions
    }
    eco_data = {
        "estimated_revenue_leakage": financials["estimated_revenue_leakage"],
        "recoverable_penalty": financials["recoverable_penalty"],
        "health_index": health_index
    }
    
    report_json = reporting.generate_audit_report(project_id, audit_data, comp_data, eco_data)
    
    # COMPATIBILITY LAYER FOR FRONTEND
    # Map new deep metrics to old frontend structure
    results = {
        "project_id": project_id,
        "timestamp": datetime.now().isoformat(),
        "change_detection": {
            "total_pixels": w*h,
            "changed_pixels": compliance_metrics["encroached_px"],
            "change_percentage": compliance_metrics["encroachment_pct"],
            "severity": risk_score["level"].lower().replace(' ', '_'), # e.g. moderate_risk
            "status": classification.lower().replace(' ', '_'), # e.g. vacant, fully_constructed
            "num_change_regions": 1 if compliance_metrics["encroachment_pct"] > 0 else 0, # Simplified
            "change_regions": [], # Could populate with contour list
            "approved_area_px": compliance_metrics["approved_px"],
            # New Metrics exposed in extra fields
            "industrial_health_index": health_index,
            "financial_impact": financials
        },
        "outputs": {
            "heatmap": f"/results/{project_id}/heatmap.png",
            "annotated": f"/results/{project_id}/annotated.png",
            "comparison": f"/results/{project_id}/comparison.png",
            "mask": f"/results/{project_id}/mask.png",
        },
        "compliance_score": int(health_index), # Reuse health index as score
        "audit_report": report_json
    }
    
    with open(os.path.join(result_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    return results

def generate_legacy_overlay(sat_img, plot_mask, encroachment_mask):
    """Helper to generate visuals (Green Outline + Red Fill)"""
    overlay = sat_img.copy()
    red_layer = np.zeros_like(overlay)
    red_layer[encroachment_mask > 0] = [0, 0, 255]
    
    contours, _ = cv2.findContours(plot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (0, 255, 0), 3)
    
    mask_indices = np.where(encroachment_mask > 0)
    if len(mask_indices[0]) > 0:
        cv2.addWeighted(overlay, 0.6, red_layer, 0.4, 0, overlay)
        
    return overlay, None


# --- Project Management Helpers (Unchanged) ---

def create_project(ref_bytes, ref_filename, sat_bytes, sat_filename, project_name=None):
    project_id = str(uuid.uuid4())[:8]
    ref_path = save_upload(ref_bytes, f"reference_{ref_filename}", project_id)
    sat_path = save_upload(sat_bytes, f"satellite_{sat_filename}", project_id)
    
    project_info = {
        "id": project_id,
        "name": project_name or f"Project-{project_id}",
        "created_at": datetime.now().isoformat(),
        "reference_image": ref_path,
        "satellite_image": sat_path,
        "status": "uploaded",
        "results": None,
    }
    
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json"), "w") as f:
        json.dump(project_info, f, indent=2)
        
    return project_info

def run_analysis(project_id):
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json")) as f:
        project = json.load(f)
        
    results = detect_changes(project["reference_image"], project["satellite_image"], project_id)
    
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
