import json
import os
import cv2
import numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.affinity import scale, translate

# Configuration
DUMP_FILE = "../csidc_dump.json"
REGISTRY_FILE = "registry.json"
THUMBNAIL_DIR = "thumbnails"
OUTPUT_SIZE = (400, 300) # Width, Height
PADDING = 0.1 # 10% padding

def create_thumbnail(geom, output_path):
    """
    Generates a visual thumbnail for a Shapely geometry using OpenCV.
    """
    minx, miny, maxx, maxy = geom.bounds
    w_geo = maxx - minx
    h_geo = maxy - miny
    
    # Aspect ratios
    aspect_geo = w_geo / h_geo
    aspect_img = OUTPUT_SIZE[0] / OUTPUT_SIZE[1]
    
    # Coordinate collection for scaling
    pts = []
    
    # Helper to process polygon coords
    def extract_exterior_coords(polygon):
        if polygon.exterior:
            return list(polygon.exterior.coords)
        return []

    if isinstance(geom, Polygon):
        pts.extend(extract_exterior_coords(geom))
    elif isinstance(geom, MultiPolygon):
        for poly in geom.geoms:
            pts.extend(extract_exterior_coords(poly))
            
    if not pts:
        return

    pts = np.array(pts)
    
    # Normalize coordinates to 0-1 range based on bounds with padding
    pts_norm = pts.copy()
    pts_norm[:, 0] = (pts[:, 0] - minx) / w_geo
    pts_norm[:, 1] = (pts[:, 1] - miny) / h_geo
    
    # Flip Y (Latitude increases upwards, Image Y increases downwards)
    pts_norm[:, 1] = 1 - pts_norm[:, 1]
    
    # Scale to image fit
    scale_w = OUTPUT_SIZE[0] * (1 - 2*PADDING)
    scale_h = OUTPUT_SIZE[1] * (1 - 2*PADDING)
    
    # Preserve aspect ratio
    if aspect_geo > aspect_img:
        # Width limited
        final_w = scale_w
        final_h = scale_w / aspect_geo
    else:
        # Height limited
        final_h = scale_h
        final_w = scale_h * aspect_geo
        
    offset_x = (OUTPUT_SIZE[0] - final_w) / 2
    offset_y = (OUTPUT_SIZE[1] - final_h) / 2
    
    # Transform points to pixel coordinates
    # We need to re-process the geometry to draw it properly as polygons
    
    img = np.zeros((OUTPUT_SIZE[1], OUTPUT_SIZE[0], 3), dtype=np.uint8)
    img[:] = (30, 30, 30) # Dark gray background
    
    def transform_coords(coords):
        res = []
        for x, y in coords:
            nx = (x - minx) / w_geo
            ny = 1 - (y - miny) / h_geo # Flip Y
            
            px = int(offset_x + nx * (OUTPUT_SIZE[0] if aspect_geo > aspect_img else final_w / (nx if nx!=0 else 1) * nx) ) 
            # Simplified scaling logic:
            # Normalized (0-1) -> Scale -> Offset
            
            # Correct Logic:
            # (x_norm - 0.5) * scale + center
            
            # Let's effectively map ranges
            px = int(offset_x + nx * final_w)
            # The ny mapping needs to align with the centered final_h (0 at top of bbox)
            # ny 0 (top of bbox) -> offset_y
            # ny 1 (bottom of bbox) -> offset_y + final_h
            py = int(offset_y + (ny * final_h))
            
            res.append([px, py])
        return np.array(res, dtype=np.int32)

    polys_to_draw = []
    if isinstance(geom, Polygon):
        polys_to_draw.append(geom)
    elif isinstance(geom, MultiPolygon):
        polys_to_draw.extend(geom.geoms)
        
    for poly in polys_to_draw:
        # Exterior
        ext_pts = transform_coords(poly.exterior.coords)
        cv2.fillPoly(img, [ext_pts], (70, 150, 70)) # Green fill
        cv2.polylines(img, [ext_pts], True, (200, 200, 200), 1, cv2.LINE_AA) # White border
        
        # Interiors (Holes)
        for interior in poly.interiors:
            int_pts = transform_coords(interior.coords)
            cv2.fillPoly(img, [int_pts], (30, 30, 30)) # Back to background color
            cv2.polylines(img, [int_pts], True, (200, 200, 200), 1, cv2.LINE_AA)

    # Add Label integration? No, frontend handles labels.
    cv2.imwrite(output_path, img)

def build_registry():
    print(f"Reading {DUMP_FILE}...")
    try:
        with open(DUMP_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {DUMP_FILE} not found.")
        return

    features = data.get('features', [])
    registry = []
    
    print(f"Processing {len(features)} features...")
    
    for feature in features:
        props = feature.get('properties', {})
        uid = feature.get('id')
        name = props.get('dist_e') # District Name (English)
        
        if not uid or not name:
            continue
            
        print(f"Processing {name} ({uid})...")
        
        # Geometry Processing
        geom_dict = feature.get('geometry')
        if not geom_dict:
            continue
            
        geom = shape(geom_dict)
        
        # Calculate Metadata
        centroid = geom.centroid
        area_km2 = geom.area * 12321 # Very rough approximation for lat/lon deg2 to km2 at this latitude, primarily for sorting size
        # Actually standard deg->km conversion is complex, let's just store raw area or skip
        
        # Generate Thumbnail
        thumb_filename = f"{uid}.png"
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_filename)
        create_thumbnail(geom, thumb_path)
        
        entry = {
            "id": uid,
            "name": name,
            "type": "District",
            "centroid": {"lat": centroid.y, "lon": centroid.x},
            "thumbnail": f"/api/registry/thumbnails/{thumb_filename}",
            "property_count": len(props)
        }
        registry.append(entry)
        
    # Write Registry
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)
        
    print(f"Registry built with {len(registry)} entries at {REGISTRY_FILE}")

if __name__ == "__main__":
    # Ensure run from backend/registry directory effectively or adjust paths
    # We set CWD to backend/registry in the tool call? 
    # The script assumes standard location 'backend/registry/' and file is at '../csidc_dump.json'
    
    # We will run this from 'backend/registry'
    if not os.path.exists(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR)
        
    build_registry()
