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
