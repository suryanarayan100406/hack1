"""
PHASE 1: RASTER -> VECTOR RECONSTRUCTION
Extracts digital plot polygons from static PNG layout maps using HSV thresholding and contour approximation.
"""

import cv2
import numpy as np

import os

def process_layout_map(image_source, debug_dir: str = None):
    """
    Convert a raster layout map (PNG/JPG) into vector polygons.
    
    Args:
        image_source: Path to image (str), image bytes (bytes), or numpy array.
        debug_dir: Optional directory to save intermediate debug steps.
        
    Returns:
        total_layout_area_px: Area of the legal boundary in pixels.
        layout_polygon: List of normalized [x, y] coordinates (0-1 range).
        contours: Raw OpenCV contours for visualization.
    """
    if isinstance(image_source, str):
        img = cv2.imread(image_source)
        if img is None:
            raise ValueError(f"Could not load image: {image_source}")
    elif isinstance(image_source, bytes):
        nparr = np.frombuffer(image_source, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif isinstance(image_source, np.ndarray):
        img = image_source
    else:
        raise ValueError("Invalid image source type")
        
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define Red Color Range (Typical for plot boundaries)
    # Lower red: 0-10, Upper red: 160-180
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    boundary_mask = mask1 | mask2
    
    # Morphological cleaning to remove noise and close gaps
    kernel = np.ones((5,5), np.uint8)
    boundary_mask = cv2.morphologyEx(boundary_mask, cv2.MORPH_CLOSE, kernel)
    boundary_mask = cv2.morphologyEx(boundary_mask, cv2.MORPH_OPEN, kernel)
    
    # Detect contours
    contours, _ = cv2.findContours(boundary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return 0, [], None

    # Assume largest contour is the plot boundary
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Approximate polygon (Ramer-Douglas-Peucker)
    epsilon = 0.005 * cv2.arcLength(largest_contour, True) # 0.5% precision
    approx_poly = cv2.approxPolyDP(largest_contour, epsilon, True)
    
    # Normalize coordinates (0.0 to 1.0) for resolution independence
    normalized_poly = []
    for point in approx_poly:
        x, y = point[0]
        normalized_poly.append([float(x)/w, float(y)/h])
        
    total_area_px = cv2.contourArea(largest_contour)
    
    return total_area_px, normalized_poly, largest_contour

def normalize_polygon(polygon, width, height):
    """Normalize polygon coordinates to 0-1 range."""
    return [[float(p[0])/width, float(p[1])/height] for p in polygon]

def extract_all_plots(image_source):
    """
    Extracts ALL plot polygons from a layout map using Canny Edge + Hierarchy.
    Returns a list of polygons (normalized) and their contours.
    """
    if isinstance(image_source, str):
        img = cv2.imread(image_source)
    elif isinstance(image_source, bytes):
        nparr = np.frombuffer(image_source, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        img = image_source
        
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Preprocessing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 2. Canny Edge Detection
    v = np.median(blurred)
    sigma = 0.33
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edges = cv2.Canny(blurred, lower, upper)
    
    # 3. Morphological Closing
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # 4. Find Contours with Hierarchy
    contours, hierarchy = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    
    plot_polygons = []
    plot_contours = []
    
    if not contours:
        return [], []

    min_area = (h * w) * 0.0001
    max_area = (h * w) * 0.5

    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue
            
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        
        if len(approx) >= 3:
            normalized = []
            for point in approx:
                px, py = point[0]
                normalized.append([float(px)/w, float(py)/h])
            
            plot_polygons.append(normalized)
            plot_contours.append(cnt)
            
    return plot_polygons, plot_contours
