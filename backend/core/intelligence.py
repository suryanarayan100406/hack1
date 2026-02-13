"""
Core Intelligence Engine: Raster-to-Vector, OCR, Georeferencing, & Satellite Analysis.
"""

import cv2
import numpy as np
import math
import uuid
import pytesseract

# Try importing Tesseract; if fails, use mock
try:
    # Assuming standard Windows install path or PATH variable setup
    # If not in PATH, user needs to configure. For MVP, we catch exception.
    pytesseract.get_tesseract_version()
    HAS_OCR = True
except Exception:
    HAS_OCR = False

class IntelligenceEngine:
    def __init__(self):
        pass

    def extract_plot_polygons(self, map_image: np.ndarray) -> list:
        """
        PHASE 1: Raster-to-Vector Boundary Reconstruction.
        Extracts plot polygons from high-res map using color segmentation.
        """
        plots = []
        h, w = map_image.shape[:2]
        
        # Convert to HSV
        hsv = cv2.cvtColor(map_image, cv2.COLOR_BGR2HSV)
        
        # Identify Industrial Plots (Green/Red/Pink/Yellow common in maps)
        # For MVP, let's assume standard colors + fallback to contours
        # We'll use a broad range for "colored regions" that are not white/black
        # Or better: Edge detection + Contour Approximation
        
        gray = cv2.cvtColor(map_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dialate to close gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, c in enumerate(contours):
            area = cv2.contourArea(c)
            # Filter noise and huge bounding boxes
            if 500 < area < (w * h * 0.5):
                # Simplify polygon
                epsilon = 0.02 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                
                # Assume valid plot if it has 4-8 sides (roughly rectangular)
                if 4 <= len(approx) <= 12:
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = 0, 0
                        
                    plot_data = {
                        "id": str(uuid.uuid4())[:8],
                        "polygon_points": approx.tolist(),
                        "pixel_area": area,
                        "centroid": (cx, cy),
                        "bbox": cv2.boundingRect(c)
                    }
                    plots.append(plot_data)
                    
        return plots

    def identify_plot_ids(self, map_image: np.ndarray, plots: list) -> list:
        """
        PHASE 2: OCR-Based Plot Identification.
        Extracts ID from inside the plot polygon.
        """
        if not HAS_OCR:
            # Fallback: Assign sequential IDs or use spatial hashing
            # For demonstration, we just return plots as-is or mock IDs
            for i, p in enumerate(plots):
                p["plot_id"] = f"PLOT-{i+101}" # Mock ID
            return plots
            
        # If OCR available
        for p in plots:
             x, y, w, h = p["bbox"]
             # Crop
             roi = map_image[y:y+h, x:x+w]
             # Preprocess for OCR
             gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
             _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
             
             try:
                 text = pytesseract.image_to_string(thresh, config='--psm 6').strip()
                 if text:
                     p["plot_id"] = text
                 else:
                     p["plot_id"] = "UNKNOWN"
             except:
                 p["plot_id"] = "ERROR"
                 
        return plots

    def georeference_plots(self, plots: list, map_bounds: dict) -> list:
        """
        PHASE 3: Georeferencing (Pseudo-GIS).
        Convert pixel coordinates to Lat/Long based on known map bounds.
        map_bounds: { min_lat, min_lon, max_lat, max_lon, width_px, height_px }
        """
        # Simple Linear Interpolation
        width_px = map_bounds.get("width_px", 1000)
        height_px = map_bounds.get("height_px", 1000)
        min_lat = map_bounds.get("min_lat", 0)
        max_lat = map_bounds.get("max_lat", 0)
        min_lon = map_bounds.get("min_lon", 0)
        max_lon = map_bounds.get("max_lon", 0)
        
        lat_scale = (max_lat - min_lat) / height_px
        lon_scale = (max_lon - min_lon) / width_px
        
        for p in plots:
            centroid_px = p["centroid"]
            # Map Y is usually inverted relative to Lat (Top=Max Lat? No, usually Top=North=MaxLat)
            # Img Origin (0,0) is Top-Left. 
            # Lat/Long Origin is Bottom-Left (usually).
            # So y_px=0 -> MaxLat. y_px=H -> MinLat.
            
            lat = max_lat - (centroid_px[1] * lat_scale)
            lon = min_lon + (centroid_px[0] * lon_scale)
            
            p["coordinates"] = {"lat": lat, "lon": lon}
            
        return plots

    def analyze_satellite_builtup(self, sat_image: np.ndarray, plot_polygon: list) -> dict:
        """
        PHASE 4: Satellite Built-up Analysis.
        Detects built-up area strictly within the plot polygon.
        """
        # Create mask for the specific plot
        mask = np.zeros(sat_image.shape[:2], dtype=np.uint8)
        pts = np.array(plot_polygon, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
        
        # Crop to bbox for speed
        x, y, w, h = cv2.boundingRect(pts)
        sat_crop = sat_image[y:y+h, x:x+w]
        mask_crop = mask[y:y+h, x:x+w]
        
        if sat_crop.size == 0:
             return {"built_up_mask": None, "area": 0}

        # Detect built-up in crop
        gray = cv2.cvtColor(sat_crop, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        # Toggle: Adaptive Thresh vs Canny? 
        # Canny is better for structure edges
        edges = cv2.Canny(blurred, 50, 150)
        
        # Close gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        structure = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)
        
        # Fill
        contours, _ = cv2.findContours(structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        built_up_mask = np.zeros_like(gray)
        cv2.drawContours(built_up_mask, contours, -1, 255, -1)
        
        # Apply Plot Mask (Strict containment)
        final_built_up = cv2.bitwise_and(built_up_mask, mask_crop)
        
        return {
            "built_up_mask": final_built_up,
            "built_up_px": cv2.countNonZero(final_built_up),
            "plot_area_px": cv2.countNonZero(mask_crop)
        }
