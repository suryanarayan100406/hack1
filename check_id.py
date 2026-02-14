import json

with open('backend/registry/optimized_dump.json', 'r') as f:
    data = json.load(f)
    print("Feature Keys:", data['features'][0].keys())
    if 'id' in data['features'][0]:
        print("ID Example:", data['features'][0]['id'])
    else:
        print("ID MISSING in top level feature!")
        print("Properties:", data['features'][0].get('properties', {}).keys())
