
import os
import sys
import json
import cv2
import numpy as np

# Setup paths
sys.path.append(os.path.dirname(__file__))

from image_processing import detect_changes

REF_PATH = r"C:\Users\samai\Desktop\hackbcackup\backend\uploads\0482108a\reference_map_a4-landscape_600dpi_2026-02-13_16-43-49.png"
SAT_PATH = r"C:\Users\samai\Desktop\hackbcackup\backend\uploads\0482108a\satellite_Screenshot 2026-02-13 164412.png"
PROJ_ID = "0482108a"

print("--- START DEBUG ---")
if not os.path.exists(REF_PATH):
    print(f"Ref path missing: {REF_PATH}")
if not os.path.exists(SAT_PATH):
    print(f"Sat path missing: {SAT_PATH}")

try:
    result = detect_changes(REF_PATH, SAT_PATH, PROJ_ID)
    print("RESULT TYPE:", type(result))
    print(json.dumps(result, indent=2))
except Exception as e:
    print("EXCEPTION:", e)
    import traceback
    traceback.print_exc()

print("--- END DEBUG ---")
