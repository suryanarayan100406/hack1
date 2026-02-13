"""
PHASE 1: RASTER -> VECTOR RECONSTRUCTION
Extracts digital plot polygons from static PNG layout maps using HSV thresholding and contour approximation.
"""

import cv2
import numpy as np

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
