"""
Image Processing Engine for CSIDC Land Sentinel.
Refined for STRICT ALIGNMENT & CROPPING.

Logic:
1. Extract 'Approved Boundary' from reference map.
2. Compute Bounding Box of the approved boundary.
3. CROP both Boundary Mask and Satellite Image to this Bounding Box.
4. Detect 'Built-up Area' in the CROPPED satellite image.
5. Encroachment = Built-up area OUTSIDE the CROPPED boundary mask.
6. STRICTLY CLAMP encroachment % to 100%.
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
    Returns:
        mask (full size), bounding_box (x,y,w,h)
    """
    h, w = ref_img.shape[:2]
    
    # Standardize: Smooth + Grayscale
    gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect Red Zones (Priority)
    hsv = cv2.cvtColor(ref_img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    if cv2.countNonZero(red_mask) > (w * h * 0.01):
        # Found Red Zone
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        boundary_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        # Fill holes
        contours, _ = cv2.findContours(boundary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(boundary_mask, contours, -1, 255, -1)
    else:
        # Fallback: Largest Contour
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
            boundary_mask.fill(255) # Full image
            
    # Calculate Bounding Box
    points = cv2.findNonZero(boundary_mask)
    if points is not None:
        bx, by, bw, bh = cv2.boundingRect(points)
    else:
        bx, by, bw, bh = 0, 0, w, h
        
    return boundary_mask, (bx, by, bw, bh)


def detect_built_up(sat_crop: np.ndarray) -> np.ndarray:
    """
    Detect built-up areas inside the CROPPED satellite image.
    """
    if sat_crop.size == 0:
        return np.zeros((1, 1), dtype=np.uint8)
        
    gray = cv2.cvtColor(sat_crop, cv2.COLOR_BGR2GRAY)
    
    # Contrast Enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Edge Detection
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilate & Close to form shapes
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    
    structure = cv2.dilate(edges, kernel_dilate, iterations=2)
    structure = cv2.morphologyEx(structure, cv2.MORPH_CLOSE, kernel_close, iterations=3)
    
    # Filter by Solidity and Area
    contours, _ = cv2.findContours(structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    built_up_mask = np.zeros_like(gray)
    
    min_area = 200
    for c in contours:
        area = cv2.contourArea(c)
        if area > min_area:
            hull = cv2.convexHull(c)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = area / hull_area
                if solidity > 0.4:
                     cv2.drawContours(built_up_mask, [c], -1, 255, -1)
                     
    return built_up_mask


def compute_encroachment(boundary_crop: np.ndarray, built_up_crop: np.ndarray) -> dict:
    """
    Calculate TRUE encroachment on strictly aligned crops.
    """
    # Ensure shapes match exactly
    if boundary_crop.shape != built_up_crop.shape:
        # Resize built_up to match boundary if slight off-by-one error
        h, w = boundary_crop.shape
        built_up_crop = cv2.resize(built_up_crop, (w, h), interpolation=cv2.INTER_NEAREST)
        
    # Invert boundary: 255 = Unauthorized
    unauthorized_zone = cv2.bitwise_not(boundary_crop)
    
    # Encroachment = Built Up AND Unauthorized
    encroachment_mask = cv2.bitwise_and(built_up_crop, unauthorized_zone)
    
    # Clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    encroachment_mask = cv2.morphologyEx(encroachment_mask, cv2.MORPH_OPEN, kernel)
    
    # Metrics
    approved_px = cv2.countNonZero(boundary_crop)
    encroached_px = cv2.countNonZero(encroachment_mask)
    
    if approved_px < 1: approved_px = 1
    
    # CLAMP LOGIC
    if encroached_px > approved_px:
        encroached_px = approved_px # Cap at 100%
        
    pct = (encroached_px / approved_px) * 100.0
    
    return {
        "encroachment_pct": round(pct, 2),
        "encroached_px": int(encroached_px),
        "approved_px": int(approved_px),
        "mask": encroachment_mask
    }


def generate_overlay(sat_full: np.ndarray, boundary_full: np.ndarray, encroachment_mask: np.ndarray, bbox: tuple) -> np.ndarray:
    """
    Generate visual overlay.
    Note: encroachment_mask is TOP-LEFT cropped relative to bbox.
    Need to place it back into full image context.
    """
    h, w = sat_full.shape[:2]
    bx, by, bw, bh = bbox
    
    # Create full-size encroachment mask
    full_encroachment = np.zeros((h, w), dtype=np.uint8)
    
    # Place crop back
    # Handle edge cases where resize might have changed shape slightly
    eh, ew = encroachment_mask.shape
    # Ensure fits in bbox
    fh, fw = min(bh, eh), min(bw, ew)
    full_encroachment[by:by+fh, bx:bx+fw] = encroachment_mask[:fh, :fw]
    
    # Create visual
    overlay = sat_full.copy()
    
    # Red Fill
    red_layer = np.zeros_like(sat_full)
    red_layer[full_encroachment > 0] = [0, 0, 255]
    
    # Green Outline
    contours, _ = cv2.findContours(boundary_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (0, 255, 0), 3)
    
    # Blend
    result = overlay.copy()
    mask_indices = np.where(full_encroachment > 0)
    if len(mask_indices[0]) > 0:
        cv2.addWeighted(overlay, 0.5, red_layer, 0.5, 0, result)
        
    return result, full_encroachment


def detect_changes(ref_path: str, sat_path: str, project_id: str) -> dict:
    """
    Orchestrator.
    """
    ref_img = cv2.imread(ref_path)
    sat_img = cv2.imread(sat_path)
    
    if ref_img is None or sat_img is None:
        return {"error": "Could not load images"}
        
    # Align full images first
    h, w = ref_img.shape[:2]
    sat_aligned = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    
    # 1. Extract Boundary
    boundary_mask, bbox = extract_boundary_mask(ref_img)
    bx, by, bw, bh = bbox
    
    # 2. CROP Step
    # Crop Boundary Mask
    boundary_crop = boundary_mask[by:by+bh, bx:bx+bw]
    # Crop Satellite Image
    sat_crop = sat_aligned[by:by+bh, bx:bx+bw]
    
    # 3. Detect Built-up on CROP
    built_up_crop = detect_built_up(sat_crop)
    
    # 4. Compute Encroachment on CROP
    metrics = compute_encroachment(boundary_crop, built_up_crop)
    
    # 5. Generate Visuals (Place back on full image)
    final_overlay, full_mask = generate_overlay(sat_aligned, boundary_mask, metrics["mask"], bbox)
    
    # --- Output ---
    result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_dir, exist_ok=True)
    
    cv2.imwrite(os.path.join(result_dir, "heatmap.png"), final_overlay)
    cv2.imwrite(os.path.join(result_dir, "annotated.png"), final_overlay)
    cv2.imwrite(os.path.join(result_dir, "comparison.png"), np.hstack([ref_img, sat_aligned]))
    cv2.imwrite(os.path.join(result_dir, "mask.png"), full_mask)
    
    # Status
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
    contours, _ = cv2.findContours(full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    change_regions = []
    for i, c in enumerate(contours):
        if cv2.contourArea(c) > 200:
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
            # changed_pixels used to map to encroachment_px
            "changed_pixels": metrics["encroached_px"], 
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
