"""
Image Processing Engine for CSIDC Land Sentinel.
Redesigned to focus on BOUNDARY-BASED ENCROACHMENT detection.

Logic:
1. Extract 'Approved Boundary' from reference map (largest contour).
2. Detect 'Built-up Area' in satellite image (edges -> dilated structure).
3. Encroachment = Built-up area physically OUTSIDE the approved boundary.
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


def create_boundary_mask(ref_img: np.ndarray) -> tuple:
    """
    Extract the approved industrial boundary polygon from the reference map.
    Returns:
        mask (numpy array): Binary mask where 255=inside boundary, 0=outside.
        contour (numpy array): The specific boundary contour found.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    
    # Pre-processing to remove noise/artifacts
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Thresholding: Assume reference map is dark lines on light background or vice versa
    # We try Otsu's binarization after inversion to find the "shape"
    # If the map is white background (high mean), we invert
    if np.mean(gray) > 127:
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
    else:
        _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Fallback: full image if no contour found
        h, w = ref_img.shape[:2]
        # In this case, mask is all white (everything is allowed) -> 0 encroachment
        return np.full((h, w), 255, dtype=np.uint8), None

    # Assume the LARGEST contour is the plot boundary
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Create clean mask
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest_contour], -1, 255, -1)  # Fill with white
    
    return mask, largest_contour


def detect_built_up(sat_img: np.ndarray) -> np.ndarray:
    """
    Detect built-up areas ONLY in the satellite image.
    Uses edge detection + morphological closing to find structures.
    Returns:
        mask (numpy array): Binary mask where 255=built-up, 0=open ground.
    """
    gray = cv2.cvtColor(sat_img, cv2.COLOR_BGR2GRAY)
    
    # 1. CLAHE for lighting normalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 2. Bilateral Filter to remove noise while keeping edges
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # 3. Canny Edge Detection to find structure boundaries
    # Dynamic thresholds based on median intensity
    v = np.median(filtered)
    lower = int(max(0, 0.66 * v))
    upper = int(min(255, 1.33 * v))
    edges = cv2.Canny(filtered, lower, upper)
    
    # 4. Morphological Closing to connect edges into solid shapes
    # This turns "lines" of a building into a "blob"
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close, iterations=2)
    
    # 5. Dilation to fill gaps
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(closed, kernel_dilate, iterations=2)
    
    # 6. Fill holes to make solid masks
    # Find contours of the "structures" and fill them
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    built_up_mask = np.zeros_like(gray)
    min_building_area = 200 # Ignore small noise (cars, rocks)
    
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_building_area]
    cv2.drawContours(built_up_mask, valid_contours, -1, 255, -1)
    
    return built_up_mask


def calculate_encroachment(boundary_mask: np.ndarray, built_up_mask: np.ndarray) -> dict:
    """
    Calculate encroachment metrics.
    Encroachment = Built-up pixels physically OUTSIDE the boundary mask.
    """
    # Invert boundary mask: 255 where it is OUTSIDE the plot
    outside_zone = cv2.bitwise_not(boundary_mask)
    
    # Encroachment = Built Up AND Outside Zone
    encroachment_mask = cv2.bitwise_and(built_up_mask, outside_zone)
    
    # Calculate areas
    approved_area_px = cv2.countNonZero(boundary_mask)
    encroachment_area_px = cv2.countNonZero(encroachment_mask)
    
    # Safety: Avoid division by zero
    if approved_area_px == 0:
        approved_area_px = 1 
        
    # Encroachment %
    encroachment_pct = (encroachment_area_px / approved_area_px) * 100
    encroachment_pct = min(encroachment_pct, 100.0) # Cap at 100%
    
    return {
        "encroachment_pct": round(encroachment_pct, 2),
        "encroachment_area_px": int(encroachment_area_px),
        "approved_area_px": int(approved_area_px),
        "encroachment_mask": encroachment_mask
    }


def generate_heatmap(sat_img: np.ndarray, encroachment_mask: np.ndarray, boundary_contour: np.ndarray) -> np.ndarray:
    """
    Generate a heatmap overlay showing encroachment.
    Green Line = Approved Boundary.
    Red Glow = Encroachment areas.
    """
    # Create red heatmap for encroachment
    heatmap = np.zeros_like(sat_img)
    heatmap[encroachment_mask > 0] = [0, 0, 255] # Red
    
    # Blend with satellite image
    # Weight: 0.7 source, 0.3 red overlay
    blended = cv2.addWeighted(sat_img, 0.7, heatmap, 0.5, 0)
    
    # Draw the approved boundary in GREEN
    if boundary_contour is not None:
        cv2.drawContours(blended, [boundary_contour], -1, (0, 255, 0), 3)
        
    return blended


def detect_changes(ref_path: str, sat_path: str, project_id: str) -> dict:
    """
    Main orchestration function matching the requested modular logic.
    """
    # Load images
    ref_img = cv2.imread(ref_path)
    sat_img = cv2.imread(sat_path)
    
    if ref_img is None or sat_img is None:
        return {"error": "Could not load images"}
        
    # Align satellite to reference (simple resize mask approach assumes roughly same aspect/scale)
    # Ideally should use feature matching, but resizing is requested MVP standard
    h, w = ref_img.shape[:2]
    sat_aligned = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    
    # 1. Create Boundary Mask
    boundary_mask, boundary_contour = create_boundary_mask(ref_img)
    
    # 2. Detect Built-up Areas
    built_up_mask = detect_built_up(sat_aligned)
    
    # 3. Calculate Encroachment
    metrics = calculate_encroachment(boundary_mask, built_up_mask)
    
    # 4. Generate Visualizations
    heatmap_img = generate_heatmap(sat_aligned, metrics["encroachment_mask"], boundary_contour)
    
    # --- Generate Outputs & Save ---
    result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_dir, exist_ok=True)
    
    # Save Heatmap
    heatmap_path = os.path.join(result_dir, "heatmap.png")
    cv2.imwrite(heatmap_path, heatmap_img)
    
    # Save Mask (for debug)
    mask_path = os.path.join(result_dir, "mask.png")
    cv2.imwrite(mask_path, metrics["encroachment_mask"])
    
    # Save Comparison (Side by Side)
    comparison = np.hstack([ref_img, sat_aligned])
    comparison_path = os.path.join(result_dir, "comparison.png")
    cv2.imwrite(comparison_path, comparison)
    
    # Reuse heatmap as annotated for consistency in frontend
    annotated_path = os.path.join(result_dir, "annotated.png")
    cv2.imwrite(annotated_path, heatmap_img)
    
    # Determine Status
    pct = metrics["encroachment_pct"]
    if pct < 1.0:
        status = "compliant"
        severity = "low"
    elif pct < 10.0:
        status = "minor_deviation"
        severity = "moderate"
    elif pct < 25.0:
        status = "violation"
        severity = "high"
    else:
        status = "major_violation"
        severity = "critical"
        
    # Find change regions (encroachment zones) for JSON response
    contours, _ = cv2.findContours(metrics["encroachment_mask"], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    change_regions = []
    
    for i, c in enumerate(contours):
        if cv2.contourArea(c) > 100:
            x, y, cw, ch = cv2.boundingRect(c)
            # Area % of APPROVED area, to be consistent with main metric
            area_pct = 0
            if metrics["approved_area_px"] > 0:
                area_pct = round((cv2.contourArea(c) / metrics["approved_area_px"]) * 100, 3)
                
            change_regions.append({
                "id": i + 1,
                "bbox": {"x": int(x), "y": int(y), "w": int(cw), "h": int(ch)},
                "area_px": int(cv2.contourArea(c)),
                "area_pct": area_pct
            })
            
    # Compile Results
    results = {
        "project_id": project_id,
        "timestamp": datetime.now().isoformat(),
        "image_dimensions": {"width": w, "height": h},
        "change_detection": {
            "total_pixels": w * h,
            "changed_pixels": metrics["encroachment_area_px"], # Using encroachment area as 'change'
            "change_percentage": metrics["encroachment_pct"],
            "severity": severity,
            "status": status,
            "num_change_regions": len(change_regions),
            "change_regions": change_regions[:20],
            "approved_area_px": metrics["approved_area_px"],
            "built_area_change_pct": 0 # Not using this metric in new logic
        },
        "outputs": {
            "heatmap": f"/results/{project_id}/heatmap.png",
            "annotated": f"/results/{project_id}/annotated.png",
            "comparison": f"/results/{project_id}/comparison.png",
            "mask": f"/results/{project_id}/mask.png",
        },
        "compliance_score": max(0, 100 - int(metrics["encroachment_pct"] * 2)),
    }
    
    # Save JSON
    with open(os.path.join(result_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    return results

def align_images(ref_img: np.ndarray, sat_img: np.ndarray) -> tuple:
    """Helper purely for compatibility if imported elsewhere, though mostly handled in detect_changes"""
    h, w = ref_img.shape[:2]
    # Simple aspect-ratio agnostic resize for now
    sat_aligned = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    return ref_img, sat_aligned

def create_project(ref_bytes: bytes, ref_filename: str,
                   sat_bytes: bytes, sat_filename: str,
                   project_name: str = None) -> dict:
    """Create a new analysis project with uploaded images."""
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

    project_dir = os.path.join(UPLOAD_DIR, project_id)
    with open(os.path.join(project_dir, "project.json"), "w") as f:
        json.dump(project_info, f, indent=2)

    return project_info


def run_analysis(project_id: str) -> dict:
    """Run change detection analysis on a project."""
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    project_file = os.path.join(project_dir, "project.json")

    if not os.path.exists(project_file):
        return {"error": f"Project {project_id} not found"}

    with open(project_file) as f:
        project = json.load(f)

    results = detect_changes(
        project["reference_image"],
        project["satellite_image"],
        project_id,
    )

    project["status"] = "analyzed"
    project["results"] = results
    with open(project_file, "w") as f:
        json.dump(project, f, indent=2)

    return results


def list_projects() -> list:
    """List all projects."""
    projects = []
    if not os.path.exists(UPLOAD_DIR):
        return projects

    for dirname in os.listdir(UPLOAD_DIR):
        project_file = os.path.join(UPLOAD_DIR, dirname, "project.json")
        if os.path.exists(project_file):
            with open(project_file) as f:
                projects.append(json.load(f))

    return sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)
