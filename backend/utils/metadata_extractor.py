import google.generativeai as genai
import os
import json
import imghdr
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"DEBUG: Gemini API Key Loaded? {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)

def log_debug(msg):
    with open("debug_gemini.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def extract_layout_metadata(image_bytes):
    """
    Analyzes a map image using Gemini 1.5 Flash to extract metadata.
    Returns a dictionary of discovered fields (name, id, area, scale).
    """
    log_debug("--- New Analysis Request ---")
    try:
        if not api_key:
            log_debug("ERROR: Gemini API Key is missing in environment.")
            return {"error": "Gemini API Key missing"}

        # Detect Mime Type
        img_type = imghdr.what(None, h=image_bytes)
        mime_type = f"image/{img_type}" if img_type else "image/jpeg"
        log_debug(f"DEBUG: Detected Image Type: {mime_type}")

        # Try multiple models in order of preference
        models_to_try = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-1.5-pro-latest',
            'gemini-pro-vision'
        ]

        response = None
        last_error = None

        for model_name in models_to_try:
            try:
                log_debug(f"DEBUG: Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content([
                    {'mime_type': mime_type, 'data': image_bytes},
                    prompt
                ])
                # If successful, break loop
                break
            except Exception as e:
                log_debug(f"WARNING: Model {model_name} failed: {e}")
                last_error = e
        
        if not response:
            raise last_error

        log_debug(f"DEBUG: Raw Gemini Response: {response.text}")
        
        # Parse output
        raw_text = response.text
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0]
            
        data = json.loads(raw_text.strip())
        log_debug(f"DEBUG: Parsed JSON: {data}")
        
        # Post-process Area to Float
        if data.get("area"):
            try:
                # Remove commas and non-numeric chars except .
                area_str = str(data["area"]).replace(",", "")
                # Extract numbers only if needed, but Gemini usually gives clean numbers
                area_val = float(area_str)
                
                unit = str(data.get("unit", "")).lower()
                
                # Convert to SQM if needed
                if "hectare" in unit or "ha" in unit:
                    area_val *= 10000
                elif "acre" in unit:
                    area_val *= 4046.86
                
                data["area"] = round(area_val, 2)
            except Exception as e:
                log_debug(f"DEBUG: Area conversion error: {e}")
                pass
                
        return data

    except Exception as e:
        log_debug(f"ERROR: Gemini Analysis failed: {e}")
        return {"error": str(e)}
