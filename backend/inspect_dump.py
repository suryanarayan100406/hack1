import json
import sys

def inspect_dump(filepath):
    print(f"Loading {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    if 'features' not in data:
        print("No 'features' key found in JSON.")
        return

    features = data['features']
    print(f"Total features found: {len(features)}")

    print("\n--- Feature Inspection (First 20) ---")
    for i, feature in enumerate(features[:20]):
        fid = feature.get('id', 'N/A')
        ftype = feature.get('type', 'N/A')
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        geom_type = geom.get('type', 'N/A')
        
        print(f"[{i}] ID: {fid} | Type: {ftype} | Geom: {geom_type}")
        if props:
            print(f"    Properties: {list(props.keys())}")
            # Print 'name' or 'district' if available
            for key in ['name', 'NAME', 'district', 'DISTRICT', 'Area', 'AREA']:
                if key in props:
                    print(f"    {key}: {props[key]}")
        else:
            print("    No Properties object found.")

if __name__ == "__main__":
    inspect_dump("c:/Users/samai/Desktop/hackbcackup/backend/csidc_dump.json")
