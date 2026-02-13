import requests
import json
import os

url = "https://cggis.cgstate.gov.in/giscg"

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
    "Authorization": "d01de439-448c-4b48-ac5b-5700ab0274b8",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://cggis.cgstate.gov.in",
    "Referer": "https://cggis.cgstate.gov.in/csidc/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

# Payload candidates
candidates = [
    "industrial_area", "industrial_areas", 
    "csidc_industrial_area", "csidc_industrial_areas",
    "industrial_estate", "industrial_estates",
    "growth_center", "growth_centers",
    "land_bank", "land_banks",
    "csidc_land"
]

for layer in candidates:
    payload_str = json.dumps({"layerName": layer})
    print(f"Testing Layer: '{layer}'...")
    
    try:
        response = requests.post(url, headers=headers, data=payload_str, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                if 'features' in data and len(data['features']) > 0:
                    print(f"SUCCESS! Found {len(data['features'])} features for '{layer}'")
                    with open(f"csidc_{layer}.json", "wb") as f:
                        f.write(response.content)
                    break # Stop on first match
                else:
                     print(f"  (200 OK but no features/invalid)")
            except:
                print("  (200 OK but not JSON)")
        else:
            print(f"  Failed ({response.status_code})")
    except Exception as e:
        print(f"  Error: {e}")
