import json
import sys
from collections import Counter

def inspect_dump(filepath, output_file):
    print(f"Loading {filepath}...")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        with open(output_file, 'w') as out:
            out.write(f"Error loading file: {e}")
        return

    if 'features' not in data:
        with open(output_file, 'w') as out:
            out.write("No 'features' key found in JSON.")
        return

    features = data['features']
    
    with open(output_file, 'w') as out:
        out.write(f"Total features found: {len(features)}\n")
        
        # Analyze feature IDs and types
        id_prefixes = Counter()
        for f in features:
            fid = f.get('id', '')
            prefix = fid.split('.')[0] if '.' in fid else 'unknown'
            id_prefixes[prefix] += 1
            
        out.write("\nFeature ID Prefixes:\n")
        for prefix, count in id_prefixes.items():
            out.write(f"  {prefix}: {count}\n")

        out.write("\n--- Sample Features (One per prefix) ---\n")
        seen_prefixes = set()
        for i, feature in enumerate(features):
            fid = feature.get('id', '')
            prefix = fid.split('.')[0] if '.' in fid else 'unknown'
            
            if prefix not in seen_prefixes:
                seen_prefixes.add(prefix)
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                geom_type = geom.get('type', 'N/A')
                
                out.write(f"\n[Index {i}] ID: {fid} | Geom: {geom_type}\n")
                out.write(f"  Properties Keys: {list(props.keys())}\n")
                out.write(f"  Sample Props: {str(props)[:200]}\n") # Limit prop string length

if __name__ == "__main__":
    inspect_dump("c:/Users/samai/Desktop/hackbcackup/backend/csidc_dump.json", "c:/Users/samai/Desktop/hackbcackup/backend/dump_inspection.txt")
