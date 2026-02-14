"""
PHASE 6: FULL GIS PIPELINE ORCHESTRATOR
Integrates Vectorization, Built-up Detection, and Compliance Metrics into a single Hackathon-ready payload.
"""

import cv2
import numpy as np
import json
import os
from shapely.geometry import Polygon
from typing import Dict, Any

from utils.vectorize_layout import process_layout_map
from utils.builtup_detection import detect_builtup_areas
from compliance.metrics import (
    calculate_encroachment, 
    calculate_health_index, 
    determine_classification, 
    recommend_actions
)

# Constants for "Mock" Georeferencing (Phase 2) if real coords not provided
DEFAULT_BOUNDS = {
    "min_lat": 21.27, "max_lat": 21.28,
    "min_lng": 81.56, "max_lng": 81.57
}

def analyze_land_compliance(
    layout_path: str, 
    satellite_path: str, 
    bounds: Dict = DEFAULT_BOUNDS,
    reference_geometry = None
) -> Dict[str, Any]:
    """
    Run the full Phase 1-6 analysis pipeline.
    """
    
    # 1. Raster -> Vector (Layout)
    if reference_geometry:
        # Use provided geometry (Shapely)
        # Normalize coords to 0-1 based on its own bounds (Fit to Screen)
        minx, miny, maxx, maxy = reference_geometry.bounds
        w_geo, h_geo = maxx - minx, maxy - miny
        
        normalized_poly = []
        
        def normalize_coords(coords):
            return [((x - minx)/w_geo, (y - miny)/h_geo) for x, y in coords]

        if reference_geometry.geom_type == 'Polygon':
            normalized_poly = normalize_coords(reference_geometry.exterior.coords)
        elif reference_geometry.geom_type == 'MultiPolygon':
            # Take convex hull or largest poly for main boundary visualization
            # Ideally support MultiPolygon in downstream, but for now take convex hull exterior
            normalized_poly = normalize_coords(reference_geometry.convex_hull.exterior.coords)
            
        layout_area_px = 0 # Ignored
        print(f"DEBUG: Using Registry Geometry for {layout_path}")
        
    else:
        # Returns normalized polygon (0-1)
        layout_area_px, normalized_poly, _ = process_layout_map(layout_path)
        
        if not normalized_poly:
            # Fallback: Use full image as boundary
            print("DEBUG: Layout vectorization failed. Using full image as boundary.")
            normalized_poly = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
            layout_area_px = 0 # Will be recalculated properly later or mocked

    # Load Satellite Image to get dimensions
    sat_img = cv2.imread(satellite_path)
    if sat_img is None:
        return {"error": "Could not load satellite image"}
    sh, sw = sat_img.shape[:2]

    # Convert normalized layout polygon to Satellite Pixel Coordinates
    # Assumption: Layout image & Satellite image cover the same ROI
    # In a real system, we'd use the Lat/Lng bounds to map them.
    # Here we perform "Strict Alignment" by scaling layout to satellite size.
    layout_poly_px = [(p[0]*sw, p[1]*sh) for p in normalized_poly]
    layout_shapely = Polygon(layout_poly_px)
    
    if not layout_shapely.is_valid:
        layout_shapely = layout_shapely.buffer(0)

    # NEW: Create ROI Mask from Layout Polygon to restrict detection
    # This prevents detecting "Forests" or "Roads" outside the plot as encroachement.
    roi_mask = np.zeros((sh, sw), dtype=np.uint8)
    if layout_poly_px:
        pts = np.array(layout_poly_px, dtype=np.int32)
        cv2.fillPoly(roi_mask, [pts], 255)

    # 2. Satellite Built-up Detection (Now with ROI)
    builtup_polys, builtup_mask = detect_builtup_areas(satellite_path, roi_mask=roi_mask)
    
    # 3. Compliance Metrics (Shapely)
    metrics = calculate_encroachment(layout_shapely, builtup_polys)
    
    # 4. Advanced Intelligence
    health_index = calculate_health_index(metrics)
    classification = determine_classification(metrics)
    actions = recommend_actions(classification, health_index)
    
    # 5. Financial Estimate (Phase 5)
    # Mock rates for hackathon
    PENALTY_RATE_PER_SQM = 500
    pixel_to_sqm_factor = 0.1 # Mock scale factor
    
    encroached_sqm = metrics["encroached_area"] * pixel_to_sqm_factor
    recoverable_penalty = encroached_sqm * PENALTY_RATE_PER_SQM
    
    # 6. Visualization Assets
    # Generate Heatmap (Red on Encroached parts)
    heatmap = np.zeros((sh, sw, 3), dtype=np.uint8)
    
    # Draw encroachment polygons in Red
    for poly in metrics["encroachment_polygons"]:
        if poly.is_empty: continue
        
        # Handle MultiPolygon or Polygon
        if poly.geom_type == 'MultiPolygon':
            geoms = poly.geoms
        else:
            geoms = [poly]
            
        for geom in geoms:
            pts = np.array(geom.exterior.coords, dtype=np.int32)
            cv2.fillPoly(heatmap, [pts], (0, 0, 255)) # Red
            
    # Draw Approved Boundary in Green
    boundary_pts = np.array(layout_poly_px, dtype=np.int32)
    cv2.polylines(heatmap, [boundary_pts], True, (0, 255, 0), 3)
    
    # Blend with original satellite
    alpha = 0.5
    blended = cv2.addWeighted(sat_img, 1-alpha, heatmap, alpha, 0)
    
    # Save result image
    result_filename = f"analysis_result_{os.path.basename(satellite_path)}"
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    if not os.path.exists(results_dir): os.makedirs(results_dir)
    cv2.imwrite(os.path.join(results_dir, result_filename), blended)
    
    return {
        "metrics": {
            "total_pixels": sw * sh,
            "approved_area_px": metrics["approved_area"],
            "builtup_area_px": metrics["builtup_area"],
            "encroached_area_px": metrics["encroached_area"],
            "encroachment_pct": round(metrics["encroachment_pct"], 2),
        },
        "intelligence": {
            "health_index": round(health_index, 1),
            "classification": classification,
            "financial": {
                "estimated_penalty": round(recoverable_penalty, 2),
                "currency": "INR"
            },
            "actions": actions
        },
        "visuals": {
            "result_image": f"/results/{result_filename}"
        },
        "gis_data": {
            "layout_polygon": normalized_poly, # GeoJSON-ready
            "crs": "EPSG:4326 (Mock)"
        }
    }
