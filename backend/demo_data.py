"""
Demo data for CSIDC Land Sentinel MVP.
Dynamic Data Provider:
- Industrial Areas: Fetched from 'registry/registry.json' (Admin Uploads)
- Plots/Analysis: Fetched from 'uploads/' (Live Analysis Projects)
"""

from image_processing import list_projects, get_official_layouts

def get_industrial_areas():
    """Fetch industrial areas from registry and format for frontend."""
    # Ensure default areas if registry is empty? 
    # User cleared registry, so it might be empty.
    # If empty, frontend might show nothing.
    registry = get_official_layouts()
    
    areas = []
    for reg in registry:
        # Calculate center from coordinates
        coords = reg.get("coordinates", [])
        center = [21.2787, 81.6528] # Default Raipur
        if coords and len(coords) > 0:
            lats = [c[0] for c in coords]
            lngs = [c[1] for c in coords]
            center = [sum(lats)/len(lats), sum(lngs)/len(lngs)]
            
        areas.append({
            "id": reg["id"],
            "name": reg["name"],
            "city": reg.get("category", "Industrial Area"),
            "center": center,
            "zoom": 15,
            "total_area_acres": round(reg.get("approved_area_sqm", 0) * 0.000247105, 1),
            "established": "2024"
        })
    return areas

# Expose as global for import (but it's dynamic now, callers should call function?)
# Frontend/API expects a list. 
# We'll make INDUSTRIAL_AREAS a property or call get_industrial_areas() in fetching functions.
# But existing code imports INDUSTRIAL_AREAS.
# We'll set it at module level, but it won't auto-update if strictly imported.
# However, in FastAPI `routes.py`, we can call `get_dashboard_stats` which uses the fresh data.
# BEWARE: `demo_data.INDUSTRIAL_AREAS` import in routes.py might be stale if module cached.
# But `routes.py` `get_demo_data` endpoint calls `get_dashboard_stats`.
# I should update `get_dashboard_stats` to return `areas`.
# And `routes.py` should look there.

# For backward compat with `from demo_data import INDUSTRIAL_AREAS`:
# We'll initialize it once. To support reload, uvicorn reloads module on change?
# No, only code change.
# If user uploads new layout, `registry.json` changes.
# `INDUSTRIAL_AREAS` variable won't update.
# I must change `routes.py` to call `get_industrial_areas()` instead of using the variable.

INDUSTRIAL_AREAS = get_industrial_areas() 

# Simulated plot data for demo mode (Empty after reset)
DEMO_PLOTS = []
DEMO_ALERTS = []

def get_live_plots():
    """Helper to fetch and format live projects as plots."""
    try:
        projects = list_projects()
        # Refresh registry for consistency
        registry = get_official_layouts()
        
        live_plots = []
        for proj in projects:
            if not proj.get("results"): continue
            
            plot_id = proj.get("plot_id")
            # Find approved layout
            layout = next((l for l in registry if l["id"] == plot_id), None)
            
            # If layout exists, use it. If not, fallback?
            coords = []
            approved_area = 0
            
            if layout:
                coords = layout.get("coordinates", [])
                approved_area = layout.get("approved_area_sqm", 0)
            
            # Determine status
            change_pct = proj["results"]["change_detection"]["change_percentage"]
            status = "violation" if change_pct > 0 else "compliant"
            
            change_status = proj["results"]["change_detection"]["status"]
            if "FULL" in change_status: change_status = "FULLY CONSTRUCTED"
            
            # Calculate bounds for image overlay
            lats = [c[0] for c in coords]
            lngs = [c[1] for c in coords]
            bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]] if coords else []

            live_plots.append({
                "id": proj["id"],
                "name": proj["name"],
                "area_id": plot_id, # Link to the Registry ID
                "status": status,
                "classification": change_status,
                "violation_type": "encroachment" if status == "violation" else None,
                "deviation_pct": change_pct,
                "compliance_score": proj["results"]["compliance_score"],
                "allotted_area_sqm": approved_area,
                "current_area_sqm": 0,
                "coordinates": coords,
                "bounds": bounds,
                "overlay_url": proj["results"]["outputs"]["heatmap"] if status == "violation" else None, # Overlay if violation
                "lease_status": "current",
                "last_payment": "2026-01-01",
                "last_checked": proj["created_at"].split("T")[0]
            })
        return live_plots
    except Exception as e:
        print(f"Error fetching live plots: {e}")
        return []


def get_dashboard_stats():
    """Compute dashboard KPI stats from demo data."""
    # Refresh areas dynamically
    current_areas = get_industrial_areas()
    
    live_plots = get_live_plots()
    all_plots = DEMO_PLOTS + live_plots
    
    total = len(all_plots)
    compliant = sum(1 for p in all_plots if p["status"] == "compliant")
    violations = sum(1 for p in all_plots if p["status"] == "violation")
    vacant = sum(1 for p in all_plots if p["status"] == "vacant")
    pending = sum(1 for a in DEMO_ALERTS if not a["acknowledged"])

    total_allotted = sum(p["allotted_area_sqm"] for p in all_plots)
    total_current = sum(p["current_area_sqm"] for p in all_plots)
    avg_compliance = sum(p["compliance_score"] for p in all_plots) / total if total else 0

    # Per-area stats
    area_stats = {}
    for area in current_areas:
        area_plots = [p for p in all_plots if p.get("area_id") == area["id"]]
        if area_plots:
            area_stats[area["id"]] = {
                "name": area["name"],
                "total_plots": len(area_plots),
                "compliant": sum(1 for p in area_plots if p["status"] == "compliant"),
                "violations": sum(1 for p in area_plots if p["status"] == "violation"),
                "vacant": sum(1 for p in area_plots if p["status"] == "vacant"),
                "avg_compliance": round(
                    sum(p["compliance_score"] for p in area_plots) / len(area_plots), 1
                ),
            }

    return {
        "total_plots": total,
        "compliant": compliant,
        "violations": violations,
        "vacant": vacant,
        "pending_alerts": pending,
        "total_allotted_sqm": total_allotted,
        "total_current_sqm": total_current,
        "avg_compliance_score": round(avg_compliance, 1),
        "area_stats": area_stats,
        "areas": current_areas, # Send dynamic areas to frontend
        "plots": all_plots # Send all plots
    }


def get_plots_geojson(area_id=None):
    """Convert plots to GeoJSON format for map display."""
    
    live_plots = get_live_plots() # Restore missing call
    
    # Merge Registry Plots (Base Layer) + Live Analysis (Overlays)
    # 1. Create a dict of analyzed plot IDs to avoid duplicates or to merge data
    analyzed_ids = {p["area_id"]: p for p in live_plots}
    
    registry = get_official_layouts()
    
    # 2. Build complete list: Start with Registry items
    combined_plots = []
    
    for reg in registry:
        # Check if we have an analysis for this registry item
        if reg["id"] in analyzed_ids:
            # Use the analyzed version (contains status, details, overlay)
            combined_plots.append(analyzed_ids[reg["id"]])
        else:
            # Add as raw/vacant plot
            # Ensure coordinates loop is closed for polygon
            coords = reg.get("coordinates", [])
            # Bounds for raw plot?
            lats = [c[0] for c in coords]
            lngs = [c[1] for c in coords]
            bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]] if coords else []
            
            combined_plots.append({
                "id": reg["id"], # Use registry ID
                "name": reg["name"],
                "area_id": reg["id"], # Self-reference or parent area?
                "status": "vacant", # Default status
                "classification": "UNANALYZED",
                "violation_type": None,
                "deviation_pct": 0,
                "compliance_score": 100,
                "allotted_area_sqm": reg.get("approved_area_sqm", 0),
                "current_area_sqm": 0,
                "coordinates": coords,
                "bounds": bounds,
                "overlay_url": None, # No heatmap
                "lease_status": "active",
                "last_payment": "-",
                "last_checked": "Not Scanned"
            })
            
    # Add any live plots that might not match a registry ID (edge case)
    # (Optional, but good for robustness)
    
    plots = combined_plots
    if area_id and area_id != "all":
        plots = [p for p in plots if p.get("area_id") == area_id]

    features = []
    for plot in plots:
        coords = plot["coordinates"]
        if not coords: continue
        
        # Close the polygon
        ring = [[c[1], c[0]] for c in coords]  # GeoJSON uses [lng, lat]
        if not ring: continue
        if ring[0] != ring[-1]:
            ring.append(ring[0])

        feature = {
            "type": "Feature",
            "properties": {
                "id": plot["id"],
                "name": plot["name"],
                "status": plot["status"],
                "violation_type": plot["violation_type"],
                "deviation_pct": plot["deviation_pct"],
                "compliance_score": plot["compliance_score"],
                "allotted_area_sqm": plot["allotted_area_sqm"],
                "current_area_sqm": plot["current_area_sqm"],
                "lease_status": plot["lease_status"],
                "last_payment": plot["last_payment"],
                "last_checked": plot["last_checked"],
                "area_id": plot["area_id"],
                "overlay_url": plot.get("overlay_url"),
                "bounds": plot.get("bounds")
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [ring],
            },
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}
