import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def test_flow():
    # 1. Simulate Admin Upload (Create Registry Entry)
    print("1. Uploading Layout via Admin...")
    # Create a dummy image
    import cv2
    import numpy as np
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (90, 90), (0, 0, 255), 2) # Red box
    cv2.imwrite("test_layout.png", img)
    
    with open("test_layout.png", "rb") as f:
        files = {"file": f}
        data = {
            "id": "TEST-PLOT-001",
            "name": "Test Plot Alpha",
            "category": "Industrial",
            "approved_area": 5000,
            "lat_min": 21.00,
            "lat_max": 21.01,
            "lng_min": 81.00,
            "lng_max": 81.01
        }
        res = requests.post(f"{BASE_URL}/admin/upload-layout", files=files, data=data)
        if res.status_code == 200:
            print("   SUCCESS: Admin Upload")
        else:
            print(f"   FAIL: {res.text}")
            return

    # 2. Check GeoJSON (Should appear as Vacant)
    print("\n2. Checking Map GeoJSON...")
    res = requests.get(f"{BASE_URL}/geojson")
    geojson = res.json()
    found = False
    for feature in geojson["features"]:
        if feature["properties"]["id"] == "TEST-PLOT-001":
            print(f"   SUCCESS: Found Plot on Map. Status: {feature['properties']['status']}")
            found = True
            break
    if not found:
        print("   FAIL: Plot not found in GeoJSON")
        return

    # 3. Simulate Analysis (Create Project)
    print("\n3. Simulating Analysis...")
    # Upload 'Satellite' image matching the layout
    with open("test_layout.png", "rb") as f:
        files = {"satellite": f}
        data = {"plot_id": "TEST-PLOT-001", "project_name": "Test Analysis"}
        res = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        if res.status_code != 200:
             print(f"   FAIL Upload: {res.text}")
             return
        
        project_id = res.json()["project"]["id"]
        
        # Trigger Analyze
        res = requests.post(f"{BASE_URL}/analyze/{project_id}")
        if res.status_code == 200:
            print("   SUCCESS: Analysis Complete")
        else:
             print(f"   FAIL Analyze: {res.text}")
             return

    # 4. Check GeoJSON Again (Should update status)
    print("\n4. Checking Map GeoJSON for Updates...")
    res = requests.get(f"{BASE_URL}/geojson")
    geojson = res.json()
    for feature in geojson["features"]:
        if feature["properties"]["id"] == "TEST-PLOT-001":
            status = feature["properties"]["status"]
            print(f"   SUCCESS: Plot Status is now: {status}")
            if status != "vacant":
                print("   VERIFIED: Map updated after analysis.")
            else:
                print("   WARNING: Status did not change (maybe no violation found?)")

if __name__ == "__main__":
    test_flow()
