"""
Image Processing Engine for CSIDC Land Sentinel.
Refined for ROBUST BOUNDARY-BASED ENCROACHMENT detection.

Logic:
1. Extract 'Approved Boundary' from reference map.
   - Priority: Detect RED zones (industrial plots).
   - Fallback: Largest contour if no color detected.
2. Detect 'Built-up Area' in satellite image inside the ROI.
3. Encroachment = Built-up area physically OUTSIDE the approved boundary mask.
4. Strict clamping and noise filtering.
"""

import cv2
import numpy as np
import os
import json
import uuid
from datetime import datetime

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str, project_id: str) -> str:
    """Save an uploaded file and return the path."""
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    filepath = os.path.join(project_dir, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)
    return filepath


def extract_boundary_mask(ref_img: np.ndarray) -> tuple:
    """
    Extract the approved industrial boundary mask.
    Priority 1: Detect RED color regions (typical for industrial zone maps).
    Priority 2: Largest contour (fallback for B/W maps).
    Returns:
        mask (full size), bounding_box (x,y,w,h)
    """
    h, w = ref_img.shape[:2]
    
    # Convert to HSV for color detection
    hsv = cv2.cvtColor(ref_img, cv2.COLOR_BGR2HSV)
    
    # Define RED color range (Industrial zones are often marked red)
    # Range 1: 0-10 (Red)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    # Range 2: 170-180 (Red wrap-around)
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # Check if we found significant red areas (> 1% of image)
    if cv2.countNonZero(red_mask) > (w * h * 0.01):
        # Found red zones! Use them as boundary.
        # Morphological closing to fill small gaps and connect plots
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        boundary_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        # Fill holes
        contours, _ = cv2.findContours(boundary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(boundary_mask, contours, -1, 255, -1)
    else:
        # Fallback: Use largest contour method (for B/W or non-standard maps)
        gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Otsu thresholding
        if np.mean(gray) > 127: # Light background
            _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
        else: # Dark background
            _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)
            
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boundary_mask = np.zeros((h, w), dtype=np.uint8)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            cv2.drawContours(boundary_mask, [largest], -1, 255, -1)
        else:
            boundary_mask.fill(255) # Full image if detection fails
            
    # Calculate Bounding Box of the boundary
    # This helps us crop/focus the satellite analysis
    points = cv2.findNonZero(boundary_mask)
    if points is not None:
        bx, by, bw, bh = cv2.boundingRect(points)
    else:
        bx, by, bw, bh = 0, 0, w, h
        
    return boundary_mask, (bx, by, bw, bh)


def detect_built_up(sat_img: np.ndarray, roi_bbox: tuple) -> np.ndarray:
    """
    Detect built-up areas inside the satellite image.
    Strictly focuses on the Region of Interest (ROI) to reduce noise.
    """
    h, w = sat_img.shape[:2]
    bx, by, bw, bh = roi_bbox
    
    # Create a blank mask
    built_up_mask = np.zeros((h, w), dtype=np.uint8)
    
    # Extract ROI from satellite image
    roi = sat_img[by:by+bh, bx:bx+bw]
    if roi.size == 0:
        return built_up_mask
        
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # 1. Enhance contrast (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(roi_gray)
    
    # 2. Edge Detection (Canny)
    # Good for finding buildings/walls/roads
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # 3. Morphological Dilate & Close -> "Smear" edges into solid blobs
    # This connects the walls of a building into a solid building shape
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    
    # Dilate edges to connect them
    structure = cv2.dilate(edges, kernel_dilate, iterations=2)
    # Close large gaps (fill inside of buildings)
    structure = cv2.morphologyEx(structure, cv2.MORPH_CLOSE, kernel_close, iterations=3)
    
    # 4. Fill Holes
    contours_roi, _ = cv2.findContours(structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter noise based on size and "solidity" (to ignore thin messy lines like loose roads/wires)
    min_area = 500
    
    roi_mask = np.zeros_like(roi_gray)
    for c in contours_roi:
        area = cv2.contourArea(c)
        if area > min_area:
            # Check solidity (Area / Convex Hull Area)
            # Buildings are usually solid/convex. Messy noise is often sparse.
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = area / hull_area
                # If too "hollow" or "spidery", ignore it (e.g. vegetation noise)
                # But be careful not to ignore L-shaped buildings.
                # Threshold > 0.4 is usually safe for buildings.
                if solidity > 0.4:
                    cv2.drawContours(roi_mask, [c], -1, 255, -1)
    
    # Place ROI mask back into full-size mask
    built_up_mask[by:by+bh, bx:bx+bw] = roi_mask
    
    return built_up_mask


def compute_encroachment(boundary_mask: np.ndarray, built_up_mask: np.ndarray) -> dict:
    """
    Calculate TRUE encroachment.
    Encroachment = Built_up_Mask AND (NOT Boundary_Mask).
    """
    # Simply: Where is it built, but NOT approved?
    # Invert boundary: 255 = Unauthorized zone
    unauthorized_zone = cv2.bitwise_not(boundary_mask)
    
    # Encroachment
    encroachment_mask = cv2.bitwise_and(built_up_mask, unauthorized_zone)
    
    # Clean up encroachment mask (remove tiny specks)
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    encroachment_mask = cv2.morphologyEx(encroachment_mask, cv2.MORPH_OPEN, kernel_clean)
    
    # Calculate Pixels
    approved_px = cv2.countNonZero(boundary_mask)
    encroached_px = cv2.countNonZero(encroachment_mask)
    
    # Avoid zero div
    if approved_px < 1: approved_px = 1
        
    pct = (encroached_px / approved_px) * 100.0
    pct = min(pct, 100.0) # Clamp
    
    return {
        "encroachment_pct": round(pct, 2),
        "encroachment_px": int(encroached_px),
        "approved_px": int(approved_px),
        "mask": encroachment_mask
    }


def generate_overlay(sat_img: np.ndarray, boundary_mask: np.ndarray, encroachment_mask: np.ndarray) -> np.ndarray:
    """
    Generate the final visual result.
    Green Outline = Approved Boundary.
    Red Fill = Encroachment.
    """
    # 1. Base is satellite image
    overlay = sat_img.copy()
    
    # 2. Draw Encroachment (Red Fill with transparency)
    # Create red layer
    red_layer = np.zeros_like(sat_img)
    red_layer[encroachment_mask > 0] = [0, 0, 255] # Red
    
    # Draw Approved Boundary (Green Outline)
    contours_bound, _ = cv2.findContours(boundary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours_bound, -1, (0, 255, 0), 3) # Green line
    
    # Blend red fill
    # Only blend where encroachment exists
    result = overlay.copy()
    alpha = 0.5
    
    # Fast blending using masks
    mask_indices = np.where(encroachment_mask > 0)
    if len(mask_indices[0]) > 0:
         cv2.addWeighted(overlay, 1-alpha, red_layer, alpha, 0, result)
         
    return result


def detect_changes(ref_path: str, sat_path: str, project_id: str) -> dict:
    """
    Orchestrator for the analysis.
    """
    ref_img = cv2.imread(ref_path)
    sat_img = cv2.imread(sat_path)
    
    if ref_img is None or sat_img is None:
        return {"error": "Could not load images"}
        
    # Align
    h, w = ref_img.shape[:2]
    sat_aligned = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    
    # 1. Extract Boundary
    boundary_mask, bbox = extract_boundary_mask(ref_img)
    
    # 2. Detect Built-up (using bbox cropping logic implicitly inside)
    built_up_mask = detect_built_up(sat_aligned, bbox)
    
    # 3. Compute Encroachment
    metrics = compute_encroachment(boundary_mask, built_up_mask)
    
    # 4. Generate Visuals
    final_overlay = generate_overlay(sat_aligned, boundary_mask, metrics["mask"])
    
    # --- Output ---
    result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_dir, exist_ok=True)
    
    # Save Images
    cv2.imwrite(os.path.join(result_dir, "heatmap.png"), final_overlay)
    cv2.imwrite(os.path.join(result_dir, "annotated.png"), final_overlay) # Same for now
    cv2.imwrite(os.path.join(result_dir, "comparison.png"), np.hstack([ref_img, sat_aligned]))
    cv2.imwrite(os.path.join(result_dir, "mask.png"), metrics["mask"])
    
    # Status
    # Use configurable thresholds
    pct = metrics["encroachment_pct"]
    if pct < 1:
        status = "compliant"
        severity = "low"
    elif pct < 15:
        status = "minor_deviation"
        severity = "moderate"
    elif pct < 30:
        status = "violation"
        severity = "high"
    else:
        status = "major_violation"
        severity = "critical"
        
    # Regions
    contours, _ = cv2.findContours(metrics["mask"], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    change_regions = []
    for i, c in enumerate(contours):
        if cv2.contourArea(c) > 200: # Additional filtering
            x, y, cw, ch = cv2.boundingRect(c)
            change_regions.append({
                "id": i+1,
                "bbox": {"x": int(x), "y": int(y), "w": int(cw), "h": int(ch)},
                "area_px": int(cv2.contourArea(c)),
                "area_pct": round(cv2.contourArea(c) / metrics["approved_px"] * 100, 3)
            })
    
    results = {
        "project_id": project_id,
        "timestamp": datetime.now().isoformat(),
        "image_dimensions": {"width": w, "height": h},
        "change_detection": {
            "total_pixels": w*h,
            "changed_pixels": metrics["encroachment_px"],
            "change_percentage": metrics["encroachment_pct"],
            "severity": severity,
            "status": status,
            "num_change_regions": len(change_regions),
            "change_regions": change_regions[:20],
            "approved_area_px": metrics["approved_px"]
        },
        "outputs": {
            "heatmap": f"/results/{project_id}/heatmap.png",
            "annotated": f"/results/{project_id}/annotated.png",
            "comparison": f"/results/{project_id}/comparison.png",
            "mask": f"/results/{project_id}/mask.png",
        },
        "compliance_score": max(0, 100 - int(metrics["encroachment_pct"] * 2.5)),
    }
    
    with open(os.path.join(result_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    return results

def align_images(ref_img: np.ndarray, sat_img: np.ndarray) -> tuple:
    h, w = ref_img.shape[:2]
    sat_aligned = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    return ref_img, sat_aligned

def create_project(ref_bytes: bytes, ref_filename: str,
                   sat_bytes: bytes, sat_filename: str,
                   project_name: str = None) -> dict:
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

def run_analysis(project_id: str) -> dict:
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json")) as f:
        project = json.load(f)
        
    results = detect_changes(project["reference_image"], project["satellite_image"], project_id)
    
    project["status"] = "analyzed"
    project["results"] = results
    with open(os.path.join(UPLOAD_DIR, project_id, "project.json"), "w") as f:
        json.dump(project, f, indent=2)
        
    return results

def list_projects() -> list:
    projects = []
    if os.path.exists(UPLOAD_DIR):
        for d in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, d, "project.json")
            if os.path.exists(p):
                with open(p) as f: projects.append(json.load(f))
    return sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)
