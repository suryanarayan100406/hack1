"""
PHASE 3: SATELLITE BUILT-UP DETECTION
Extracts built-up structures from satellite imagery using Edge Detection and Morphological Filtering.
"""

import cv2
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon

def detect_builtup_areas(image_path: str, min_area_threshold: float = 0.01, roi_mask: np.ndarray = None):
    """
    Detect buildings/structures in a satellite image.
    Optionally constrained to a Region of Interest (ROI).
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
        
    h, w = img.shape[:2]
    
    # ROI Strategy: 
    # Do NOT mask the input image with black, as that creates artificial edges at the boundary (Canny picks them up).
    # Instead, compute edges on full image, then mask the edges.
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Pre-processing: Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Canny Edge Detection
    # Thresholds auto-adjusted based on median quality
    v = np.median(blurred)
    # Using stricter sigma for tighter control
    sigma = 0.33
    lower_thresh = int(max(0, (1.0 - sigma) * v))
    upper_thresh = int(min(255, (1.0 + sigma) * v))
    edges = cv2.Canny(blurred, lower_thresh, upper_thresh)
    
    # Apply ROI to edges to strictly limit detection to inside the plot
    if roi_mask is not None:
        # Ensure mask is same size
        if roi_mask.shape[:2] != (h, w):
            roi_mask = cv2.resize(roi_mask, (w, h), interpolation=cv2.INTER_NEAREST)
        edges = cv2.bitwise_and(edges, edges, mask=roi_mask)
    
    # Dilate edges to connect gaps (make walls solid)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Close operations to fill internal holes
    closing_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, closing_kernel, iterations=2)
    
    # Find contours of potential buildings
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    builtup_polygons = []
    valid_contours = []
    
    min_px_area = w * h * min_area_threshold
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_px_area:
            continue # Ignore small noise
            
        # Optional: Rectangularity check can be added here
        # rect = cv2.minAreaRect(cnt)
        # box_area = rect[1][0] * rect[1][1]
        # solidity = area / float(box_area) if box_area > 0 else 0
        
        # Convert to Shapely Polygon
        # Shapely expects a list of (x, y) tuples
        poly_points = [tuple(p[0]) for p in cnt]
        if len(poly_points) >= 3: # Valid polygon needs > 3 points
            poly = ShapelyPolygon(poly_points)
            if not poly.is_valid:
                poly = poly.buffer(0) # Fix self-intersections
                
            builtup_polygons.append(poly)
            valid_contours.append(cnt)
            
    # Create final mask for visualization
    final_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(final_mask, valid_contours, -1, 255, -1)
    
    return builtup_polygons, final_mask
