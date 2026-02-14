import json
import os
from shapely.geometry import shape

DUMP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP_FILE = os.path.join(DUMP_DIR, "csidc_dump.json")
REGISTRY_DIR = os.path.join(DUMP_DIR, "registry")
REGISTRY_FILE = os.path.join(REGISTRY_DIR, "registry.json")

def get_registry_index():
    """Returns the list of available registry items."""
    if not os.path.exists(REGISTRY_FILE):
        return []
    with open(REGISTRY_FILE, 'r') as f:
        return json.load(f)

def get_registry_geometry(item_id):
    """
    Fetches the Shapely geometry for a given registry item ID.
    Reads from the main dump file to avoid duplicating geometry data.
    """
    try:
        with open(DUMP_FILE, 'r') as f:
            data = json.load(f)
            
        for feature in data.get('features', []):
            if feature.get('id') == item_id:
                return shape(feature.get('geometry'))
                
    except Exception as e:
        print(f"Error fetching registry geometry: {e}")
        return None
    return None

def get_registry_geojson():
    """
    Returns the full registry dump as a GeoJSON FeatureCollection.
    Used for frontend map visualization.
    Prioritizes optimized file if available.
    """
    # Check for optimized file first
    optimized_path = os.path.join(REGISTRY_DIR, "optimized_dump.json")
    if os.path.exists(optimized_path):
        try:
            with open(optimized_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading optimized dump file: {e}")

    # Fallback to original
    if os.path.exists(DUMP_FILE):
        try:
            with open(DUMP_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading dump file: {e}")
    return {"type": "FeatureCollection", "features": []}
