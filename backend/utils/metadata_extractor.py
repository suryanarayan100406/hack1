import cv2
import numpy as np
import re
import pytesseract

def extract_layout_metadata(image_bytes):
    """
    Analyzes a map image to extract metadata using OCR.
    Returns a dictionary of discovered fields.
    """
    try:
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {}

        # Preprocessing for OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Thresholding (Otsu's binarization)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Run OCR
        # psm 11: Sparse text. psm 3: Fully automatic segmentation (default).
        # We try default first.
        try:
            text = pytesseract.image_to_string(binary)
        except Exception:
            # Fallback if tesseract not installed/found
            return {"error": "OCR engine not available"}
            
        print(f"OCR Extracted Text (First 100 chars): {text[:100]}")
        
        # Parse Text
        metadata = {}
        
        # 1. Industrial Area Name
        # Look for "Industrial Area", "Growth Center", "Project:"
        name_match = re.search(r"(?:Project|Name|Industrial Area|Sector)[:\s]+([A-Za-z0-9\s\-\(\)]+)", text, re.IGNORECASE)
        if name_match:
            metadata["name"] = name_match.group(1).strip()
            
        # 2. Area
        # Look for digits followed by sqm, acres, ha
        area_match = re.search(r"Total Area[:\s]+([\d\.,]+)\s*(sqm|sq\.m|m2|acres|ha)", text, re.IGNORECASE)
        if area_match:
            raw_area = area_match.group(1).replace(",", "")
            unit = area_match.group(2).lower()
            try:
                val = float(raw_area)
                # Normalize to sqm
                if "acre" in unit:
                    val *= 4046.86
                elif "ha" in unit:
                    val *= 10000
                metadata["area"] = round(val, 2)
            except:
                pass
                
        # 3. ID / Zone
        # Look for "Zone-X", "Block-Y"
        id_match = re.search(r"(Zone|Block|Phase)[\s\-]+([A-Z0-9]+)", text, re.IGNORECASE)
        if id_match:
            metadata["category_hint"] = f"{id_match.group(1)} {id_match.group(2)}"
            # Construct a potential ID
            if "name" in metadata:
                metadata["id"] = f"{metadata['name'].split()[0].upper()}-{id_match.group(1).upper()}-{id_match.group(2)}"
            else:
                metadata["id"] = f"CSIDC-{id_match.group(1).upper()}-{id_match.group(2)}"
                
        # 4. Sheet Number / Scale (Optional)
        scale_match = re.search(r"Scale\s*1\s*:\s*(\d+)", text, re.IGNORECASE)
        if scale_match:
            metadata["scale"] = f"1:{scale_match.group(1)}"
            
        return metadata

    except Exception as e:
        print(f"Metadata extraction failed: {e}")
        return {}
