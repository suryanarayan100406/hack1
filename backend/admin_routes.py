from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import json
import cv2
import numpy as np
import base64
from typing import Optional

from utils.vectorize_layout import process_layout_map

router = APIRouter(prefix="/api/admin", tags=["admin"])

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "registry", "registry.json")
LAYOUTS_DIR = os.path.join(os.path.dirname(__file__), "registry", "layouts")

os.makedirs(LAYOUTS_DIR, exist_ok=True)

@router.post("/digitize")
async def digitize_layout(file: UploadFile = File(...)):
    """
    Preview vectorization of an uploaded map.
    Returns the detected polygon and a visual overlay.
    """
    contents = await file.read()
    
    # Process image
    try:
        area_px, normalized_poly, contour = process_layout_map(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Create debug overlay image
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    
    # Draw contour
    cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)  # Green boundary
    
    # Encode to base64 for frontend preview
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "polygon": normalized_poly,
        "area_px": area_px,
        "preview_image": f"data:image/jpeg;base64,{img_base64}",
        "message": "Vectorization successful"
    }

@router.post("/upload-layout")
async def upload_layout(
    file: UploadFile = File(...),
    id: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    approved_area: float = Form(...),
    lat_min: float = Form(...),
    lat_max: float = Form(...),
    lng_min: float = Form(...),
    lng_max: float = Form(...)
):
    """
    Save a new official layout to the registry.
    """
    # 1. Save Image
    filename = f"{id}.png"
    filepath = os.path.join(LAYOUTS_DIR, filename)
    
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # 2. Start Processing for Geo-Polygon
    # Read file content again for processing (since file pointer is at end)
    await file.seek(0)
    contents = await file.read()
    
    try:
        # Get normalized polygon (0-1 range)
        _, normalized_poly, _ = process_layout_map(contents)
        
        # Transform to Geo Coordinates
        # Image (0,0) is Top-Left. Geo (LatMax, LngMin) is Top-Left.
        geo_poly = []
        lat_range = lat_max - lat_min
        lng_range = lng_max - lng_min
        
        for [x, y] in normalized_poly:
            # x (0->1) maps to Lng (Min->Max)
            # y (0->1) maps to Lat (Max->Min)
            lng = lng_min + (x * lng_range)
            lat = lat_max - (y * lat_range)
            geo_poly.append([lat, lng])
            
    except Exception as e:
        print(f"Vectorization failed: {e}. Fallback to bounding box.")
        # Fallback to simple rectangle if vectorization fails
        geo_poly = [
            [lat_min, lng_min],
            [lat_min, lng_max],
            [lat_max, lng_max],
            [lat_max, lng_min]
        ]

    # 3. Update Registry JSON
    registry_data = []
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r') as f:
            try:
                registry_data = json.load(f)
            except:
                registry_data = []
    
    # Check if ID exists
    existing = next((item for item in registry_data if item["id"] == id), None)
    if existing:
        registry_data.remove(existing)
        
    new_entry = {
        "id": id,
        "name": name,
        "category": category,
        "approved_area_sqm": approved_area,
        "coordinates": geo_poly,
        "image_path": f"layouts/{filename}"
    }
    
    registry_data.append(new_entry)
    
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry_data, f, indent=2)
        
    return {"message": "Layout saved to registry", "entry": new_entry}
