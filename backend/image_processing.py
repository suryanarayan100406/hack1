"""
Image Processing Engine for CSIDC Land Sentinel.
Performs change detection between reference maps and satellite/drone imagery.
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
    """
    Resize satellite image to match reference image dimensions.
    For MVP, we do simple resize alignment.
    """
    h, w = ref_img.shape[:2]
    sat_resized = cv2.resize(sat_img, (w, h), interpolation=cv2.INTER_AREA)
    return ref_img, sat_resized


def detect_changes(ref_path: str, sat_path: str, project_id: str) -> dict:
    """
    Perform change detection between reference and satellite images.
    Returns analysis results with annotated images.
    """
    # Load images
    ref_img = cv2.imread(ref_path)
    sat_img = cv2.imread(sat_path)

    if ref_img is None or sat_img is None:
        return {"error": "Could not load one or both images"}

    # Align images
    ref_aligned, sat_aligned = align_images(ref_img, sat_img)

    # Convert to grayscale for comparison
    ref_gray = cv2.cvtColor(ref_aligned, cv2.COLOR_BGR2GRAY)
    sat_gray = cv2.cvtColor(sat_aligned, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    ref_blur = cv2.GaussianBlur(ref_gray, (5, 5), 0)
    sat_blur = cv2.GaussianBlur(sat_gray, (5, 5), 0)

    # Compute absolute difference
    diff = cv2.absdiff(ref_blur, sat_blur)

    # Threshold the difference
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter small contours (noise)
    min_contour_area = 500
    significant_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]

    # Calculate statistics
    total_pixels = ref_aligned.shape[0] * ref_aligned.shape[1]
    changed_pixels = cv2.countNonZero(thresh)
    change_pct = round((changed_pixels / total_pixels) * 100, 2)

    # Classify severity
    if change_pct < 2:
        severity = "low"
        status = "compliant"
    elif change_pct < 10:
        severity = "moderate"
        status = "minor_deviation"
    elif change_pct < 25:
        severity = "high"
        status = "violation"
    else:
        severity = "critical"
        status = "major_violation"

    # Create annotated images
    result_dir = os.path.join(RESULTS_DIR, project_id)
    os.makedirs(result_dir, exist_ok=True)

    # 1. Difference heatmap
    heatmap = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
    heatmap_path = os.path.join(result_dir, "heatmap.png")
    cv2.imwrite(heatmap_path, heatmap)

    # 2. Contour overlay on satellite image
    overlay = sat_aligned.copy()
    for contour in significant_contours:
        area = cv2.contourArea(contour)
        if area > 2000:
            color = (0, 0, 255)  # Red for large changes
        elif area > 1000:
            color = (0, 165, 255)  # Orange for medium
        else:
            color = (0, 255, 255)  # Yellow for small
        cv2.drawContours(overlay, [contour], -1, color, 2)
        # Fill with transparency
        cv2.drawContours(overlay, [contour], -1, color, -1)

    # Blend overlay with original
    annotated = cv2.addWeighted(sat_aligned, 0.6, overlay, 0.4, 0)
    annotated_path = os.path.join(result_dir, "annotated.png")
    cv2.imwrite(annotated_path, annotated)

    # 3. Side-by-side comparison
    comparison = np.hstack([ref_aligned, sat_aligned])
    comparison_path = os.path.join(result_dir, "comparison.png")
    cv2.imwrite(comparison_path, comparison)

    # 4. Threshold mask
    mask_colored = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    mask_colored[thresh > 0] = [0, 0, 255]
    mask_path = os.path.join(result_dir, "mask.png")
    cv2.imwrite(mask_path, mask_colored)

    # Build change regions data
    change_regions = []
    for i, contour in enumerate(significant_contours):
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        change_regions.append({
            "id": i + 1,
            "bbox": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
            "area_px": int(area),
            "area_pct": round((area / total_pixels) * 100, 3),
        })

    results = {
        "project_id": project_id,
        "timestamp": datetime.now().isoformat(),
        "image_dimensions": {
            "width": ref_aligned.shape[1],
            "height": ref_aligned.shape[0],
        },
        "change_detection": {
            "total_pixels": int(total_pixels),
            "changed_pixels": int(changed_pixels),
            "change_percentage": change_pct,
            "severity": severity,
            "status": status,
            "num_change_regions": len(significant_contours),
            "change_regions": change_regions[:20],  # Top 20
        },
        "outputs": {
            "heatmap": f"/results/{project_id}/heatmap.png",
            "annotated": f"/results/{project_id}/annotated.png",
            "comparison": f"/results/{project_id}/comparison.png",
            "mask": f"/results/{project_id}/mask.png",
        },
        "compliance_score": max(0, 100 - int(change_pct * 4)),
    }

    # Save results JSON
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

    # Save project info
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

    # Update project status
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
