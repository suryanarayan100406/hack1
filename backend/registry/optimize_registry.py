import json
import os
from shapely.geometry import shape, mapping

DUMP_FILE = "../csidc_dump.json"
OPTIMIZED_FILE = "optimized_dump.json"
SIMPLIFICATION_TOLERANCE = 0.001  # Degrees. Adjust as needed. 0.001 is approx 100m

def optimize_registry():
    print(f"Reading {DUMP_FILE}...")
    try:
        with open(DUMP_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {DUMP_FILE} not found.")
        return

    features = data.get('features', [])
    optimized_features = []
    
    print(f"Optimizing {len(features)} features with tolerance {SIMPLIFICATION_TOLERANCE}...")
    
    total_original_points = 0
    total_optimized_points = 0
    
    for feature in features:
        geom = shape(feature.get('geometry'))
        
        # Simplify
        # preserve_topology=True is important to avoid invalid geometries
        simplified_geom = geom.simplify(SIMPLIFICATION_TOLERANCE, preserve_topology=True)
        
        # Stats
        if geom.geom_type == 'Polygon':
            total_original_points += len(geom.exterior.coords)
        elif geom.geom_type == 'MultiPolygon':
            total_original_points += sum(len(p.exterior.coords) for p in geom.geoms)
            
        if simplified_geom.geom_type == 'Polygon':
            total_optimized_points += len(simplified_geom.exterior.coords)
        elif simplified_geom.geom_type == 'MultiPolygon':
            total_optimized_points += sum(len(p.exterior.coords) for p in simplified_geom.geoms)
            
        new_feature = feature.copy()
        new_feature['geometry'] = mapping(simplified_geom)
        optimized_features.append(new_feature)

    output_data = {
        "type": "FeatureCollection",
        "features": optimized_features
    }
    
    with open(OPTIMIZED_FILE, 'w') as f:
        json.dump(output_data, f)
        
    print(f"Optimization Complete.")
    print(f"Original Points (approx): {total_original_points}")
    print(f"Optimized Points (approx): {total_optimized_points}")
    print(f"Saved to {OPTIMIZED_FILE}")

if __name__ == "__main__":
    optimize_registry()
