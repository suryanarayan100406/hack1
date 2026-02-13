"""
Image Processing Engine for CSIDC Land Sentinel.
Performs STRUCTURAL change detection between reference allotment maps
and satellite/drone imagery using edge-based and segmentation analysis.

Key insight: A reference allotment map (hand-drawn/CAD) and a satellite photo
will ALWAYS look different at the pixel level. What matters is:
  1. Are there NEW structures in the satellite image outside reference boundaries?
  2. Has built-up area increased beyond what was allotted?
  3. Are allotted plots left vacant (no construction detected)?

Approach:
  - Extract edges (structural boundaries) from both images
  - Segment built-up vs open areas using adaptive thresholding
  - Compare structural footprints, not raw pixels
  - Flag only regions where satellite shows structures OUTSIDE reference boundaries
"""

import cv2
import numpy as np
from PIL import Image
import io
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


def align_images(ref_img: np.ndarray, sat_img: np.ndarray) -> tuple:
    """Resize satellite image to match reference image dimensions."""
    h, w = ref_img.shape[:2]
    sh, sw = sat_img.shape[:2]
    interp = cv2.INTER_AREA if (sh * sw > h * w) else cv2.INTER_CUBIC
    sat_resized = cv2.resize(sat_img, (w, h), interpolation=interp)
    return ref_img, sat_resized


def extract_edges(img: np.ndarray) -> np.ndarray:
    """
    Extract structural edges from an image using multi-scale Canny.
    Works for both hand-drawn maps and satellite photos.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()

    # Normalize contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Bilateral filter to preserve edges while smoothing noise
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)

    # Multi-scale Canny edge detection
    # Low threshold for fine edges, high threshold for strong edges
    v = np.median(filtered)
    lower = int(max(0, 0.5 * v))
    upper = int(min(255, 1.5 * v))
    edges = cv2.Canny(filtered, lower, upper)

    # Dilate edges to connect nearby fragments
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel, iterations=2)

    return edges


def extract_built_area(img: np.ndarray) -> np.ndarray:
    """
    Segment built-up / developed areas from an image.
    Uses adaptive thresholding + morphological ops to find solid structures.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()

    # Adaptive threshold to handle varying lighting
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 21, 5
    )

    # Clean up with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # Close small gaps (connect structure parts)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=3)
    # Open to remove small noise spots
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

    return binary


def detect_changes(ref_path: str, sat_path: str, project_id: str) -> dict:
    """
    Perform STRUCTURAL change detection.

    Strategy:
    1. Extract edge maps from both reference and satellite images
    2. Extract built-up area masks from both
    3. Find edges in satellite that DON'T exist in reference (new structures)
    4. Find built-up areas in satellite that DON'T exist in reference (expansion)
    5. Combine both to identify genuine encroachment/deviation regions
    6. Calculate encroachment as % of ALLOTTED area, not total image
    """
    ref_img = cv2.imread(ref_path)
    sat_img = cv2.imread(sat_path)

    if ref_img is None or sat_img is None:
        return {"error": "Could not load one or both images"}

    # Align images to same dimensions
    ref_aligned, sat_aligned = align_images(ref_img, sat_img)
    h, w = ref_aligned.shape[:2]
    total_pixels = h * w

    # ═══════════════════════════════════════════════════════════
    # STEP 1: Edge-based structural boundary comparison
    # ═══════════════════════════════════════════════════════════
    ref_edges = extract_edges(ref_aligned)
    sat_edges = extract_edges(sat_aligned)

    # Dilate reference edges generously to create a "tolerance zone"
    # Anything within this zone is considered within approved boundaries
    tolerance_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    ref_edges_dilated = cv2.dilate(ref_edges, tolerance_kernel, iterations=2)

    # New edges = edges in satellite that are OUTSIDE the reference tolerance zone
    new_edges = cv2.bitwise_and(sat_edges, cv2.bitwise_not(ref_edges_dilated))

    # ═══════════════════════════════════════════════════════════
    # STEP 2: Built-up area segmentation comparison
    # ═══════════════════════════════════════════════════════════
    ref_built = extract_built_area(ref_aligned)
    sat_built = extract_built_area(sat_aligned)

    # Dilate reference built area as tolerance zone
    ref_built_dilated = cv2.dilate(ref_built, tolerance_kernel, iterations=2)

    # New built-up area = built area in satellite OUTSIDE reference zone
    new_built = cv2.bitwise_and(sat_built, cv2.bitwise_not(ref_built_dilated))

    # ═══════════════════════════════════════════════════════════
    # STEP 3: Combine edge and segmentation evidence
    # ═══════════════════════════════════════════════════════════
    # A pixel is "encroachment" if it shows BOTH:
    #   - new edges (structural boundary not in reference)  OR
    #   - new built-up area (construction not in reference)
    combined = cv2.bitwise_or(new_edges, new_built)

    # Heavy morphological cleanup to remove false positives
    cleanup_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, cleanup_kernel, iterations=3)
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, cleanup_kernel, iterations=2)

    # ═══════════════════════════════════════════════════════════
    # STEP 4: Extract significant deviation contours
    # ═══════════════════════════════════════════════════════════
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Only keep genuinely large contours (5000+ pixels = real structures)
    min_contour_area = 5000
    significant = [c for c in contours if cv2.contourArea(c) > min_contour_area]

    # Build clean mask from only significant contours
    deviation_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(deviation_mask, significant, -1, 255, -1)

    # ═══════════════════════════════════════════════════════════
    # STEP 5: Calculate metrics correctly
    # ═══════════════════════════════════════════════════════════
    # Reference built-up area (the "allotted" footprint)
    ref_built_area = cv2.countNonZero(ref_built)
    sat_built_area = cv2.countNonZero(sat_built)
    deviation_area = cv2.countNonZero(deviation_mask)

    # Encroachment % = deviation area relative to reference built area
    # NOT relative to total image (that dilutes the number meaninglessly)
    if ref_built_area > 0:
        encroachment_pct = round((deviation_area / ref_built_area) * 100, 2)
    else:
        # If reference has no built area, use total image as baseline
        encroachment_pct = round((deviation_area / total_pixels) * 100, 2)

    # Change in total built-up footprint
    if ref_built_area > 0:
        built_area_change_pct = round(
            ((sat_built_area - ref_built_area) / ref_built_area) * 100, 2
        )
    else:
        built_area_change_pct = 0.0

    # Classify severity based on encroachment percentage
    if encroachment_pct < 3:
        severity = "low"
        status = "compliant"
    elif encroachment_pct < 10:
        severity = "moderate"
        status = "minor_deviation"
    elif encroachment_pct < 25:
        severity = "high"
        status = "violation"
    else:
        severity = "critical"
        status = "major_violation"

    # Compliance score: starts at 100, loses points for encroachment
    compliance_score = max(0, min(100, 100 - int(encroachment_pct * 2)))

    # ═══════════════════════════════════════════════════════════
    # STEP 6: Generate output visualizations
    # ═══════════════════════════════════════════════════════════
    result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_dir, exist_ok=True)

    # --- 1. Deviation Heatmap (only encroachment areas, overlaid on satellite) ---
    heatmap_color = np.zeros_like(sat_aligned)
    heatmap_color[deviation_mask > 0] = [0, 0, 255]  # Red for encroachment
    heatmap_final = cv2.addWeighted(sat_aligned, 0.7, heatmap_color, 0.3, 0)
    # Draw contour outlines
    for contour in significant:
        cv2.drawContours(heatmap_final, [contour], -1, (0, 255, 255), 2)
    heatmap_path = os.path.join(result_dir, "heatmap.png")
    cv2.imwrite(heatmap_path, heatmap_final)

    # --- 2. Annotated overlay (satellite with boundary outlines) ---
    annotated = sat_aligned.copy()
    # Draw reference edges in GREEN (approved boundaries)
    ref_edge_color = np.zeros_like(annotated)
    ref_edge_color[ref_edges > 0] = [0, 255, 0]
    annotated = cv2.addWeighted(annotated, 0.8, ref_edge_color, 0.2, 0)
    # Draw deviation contours in RED
    for contour in significant:
        area = cv2.contourArea(contour)
        if area > 15000:
            color = (0, 0, 255)   # Red — major
        elif area > 8000:
            color = (0, 140, 255) # Orange — moderate
        else:
            color = (0, 255, 255) # Yellow — minor
        cv2.drawContours(annotated, [contour], -1, color, 3)
    annotated_path = os.path.join(result_dir, "annotated.png")
    cv2.imwrite(annotated_path, annotated)

    # --- 3. Side-by-side comparison ---
    # Add labels
    ref_display = ref_aligned.copy()
    sat_display = sat_aligned.copy()
    cv2.putText(ref_display, "REFERENCE MAP", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(sat_display, "CURRENT SATELLITE", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
    comparison = np.hstack([ref_display, sat_display])
    comparison_path = os.path.join(result_dir, "comparison.png")
    cv2.imwrite(comparison_path, comparison)

    # --- 4. Edge comparison (structural overlay) ---
    edge_vis = np.zeros_like(sat_aligned)
    edge_vis[ref_edges > 0] = [0, 255, 0]     # Green = reference boundaries
    edge_vis[sat_edges > 0] = [255, 200, 0]   # Cyan = current boundaries
    edge_vis[new_edges > 0] = [0, 0, 255]     # Red = new (not in reference)
    edge_blend = cv2.addWeighted(sat_aligned, 0.5, edge_vis, 0.5, 0)
    mask_path = os.path.join(result_dir, "mask.png")
    cv2.imwrite(mask_path, edge_blend)

    # ═══════════════════════════════════════════════════════════
    # STEP 7: Build structured results
    # ═══════════════════════════════════════════════════════════
    change_regions = []
    for i, contour in enumerate(significant):
        x, y, cw, ch = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        change_regions.append({
            "id": i + 1,
            "bbox": {"x": int(x), "y": int(y), "w": int(cw), "h": int(ch)},
            "area_px": int(area),
            "area_pct": round((area / (ref_built_area if ref_built_area > 0 else total_pixels)) * 100, 3),
        })
    change_regions.sort(key=lambda r: r["area_px"], reverse=True)

    results = {
        "project_id": project_id,
        "timestamp": datetime.now().isoformat(),
        "image_dimensions": {"width": w, "height": h},
        "change_detection": {
            "total_pixels": int(total_pixels),
            "ref_built_area_px": int(ref_built_area),
            "sat_built_area_px": int(sat_built_area),
            "deviation_area_px": int(deviation_area),
            "change_percentage": encroachment_pct,
            "built_area_change_pct": built_area_change_pct,
            "severity": severity,
            "status": status,
            "num_change_regions": len(significant),
            "change_regions": change_regions[:20],
        },
        "outputs": {
            "heatmap": f"/results/{project_id}/heatmap.png",
            "annotated": f"/results/{project_id}/annotated.png",
            "comparison": f"/results/{project_id}/comparison.png",
            "mask": f"/results/{project_id}/mask.png",
        },
        "compliance_score": compliance_score,
    }

    results_json_path = os.path.join(result_dir, "results.json")
    with open(results_json_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


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
