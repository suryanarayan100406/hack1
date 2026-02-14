import sys
import os
import cv2
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from utils.builtup_detection import detect_builtup_areas
from utils.vectorize_layout import process_layout_map

PROJECT_ID = "a8bcd1c8"
BASE_DIR = os.path.join("uploads", PROJECT_ID)
SAT_IMG = os.path.join(BASE_DIR, "satellite.png") # Or .jpg, check actual filename
REF_IMG = os.path.join(BASE_DIR, "reference.png")

# Find actual files
if not os.path.exists(SAT_IMG):
    # Try finding any image in the folder
    files = os.listdir(BASE_DIR)
    sat_files = [f for f in files if "satellite" in f]
    if sat_files: SAT_IMG = os.path.join(BASE_DIR, sat_files[0])
    
    ref_files = [f for f in files if "reference" in f]
    if ref_files: REF_IMG = os.path.join(BASE_DIR, ref_files[0])

print(f"Analyzing Project: {PROJECT_ID}")
print(f"Satellite: {SAT_IMG}")
print(f"Reference: {REF_IMG}")

# 1. Test Built-up Detection
print("\n--- Testing Built-up Detection ---")
try:
    polys, mask = detect_builtup_areas(SAT_IMG, min_area_threshold=0.001) # Try very low threshold
    print(f"Detected Polygons: {len(polys)}")
    if len(polys) == 0:
        print("NO BUILDINGS DETECTED.")
        # Check image stats
        img = cv2.imread(SAT_IMG)
        print(f"Image Shape: {img.shape}")
        print(f"Mean Intensity: {np.mean(img)}")
    else:
        for i, p in enumerate(polys):
            print(f"  Poly {i}: Area={p.area}")
except Exception as e:
    print(f"Error in detection: {e}")

# 2. Test Layout Vectorization
print("\n--- Testing Layout Vectorization ---")
try:
    area, poly, cnt = process_layout_map(REF_IMG)
    print(f"Layout Area: {area}")
    print(f"Polygon Points: {len(poly) if poly else 0}")
    if not poly:
        print("VECTORIZATION FAILED (would trigger fallback).")
except Exception as e:
    print(f"Error in vectorization: {e}")
