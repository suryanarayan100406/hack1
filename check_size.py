import os
import json
from shapely.geometry import shape, mapping

DUMP_FILE = "backend/csidc_dump.json"

if os.path.exists(DUMP_FILE):
    size_mb = os.path.getsize(DUMP_FILE) / (1024 * 1024)
    print(f"File Size: {size_mb:.2f} MB")
    
    # Check vertex count for first feature
    with open(DUMP_FILE, 'r') as f:
        data = json.load(f)
        feat = data['features'][0]
        geom = shape(feat['geometry'])
        
        # Count vertices roughly
        if geom.geom_type == 'Polygon':
            coords = len(geom.exterior.coords)
        elif geom.geom_type == 'MultiPolygon':
            coords = sum(len(p.exterior.coords) for p in geom.geoms)
        else:
            coords = 0
            
        print(f"Sample Feature Vertex Count: {coords}")
else:
    print("File not found.")
