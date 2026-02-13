"""
Demo data for CSIDC Land Sentinel MVP.
Pre-loaded industrial area coordinates and simulated plot data
from real CSIDC industrial zones in Chhattisgarh.
Enhanced with Phase 2 Intelligence Metrics (Health, Financials, Classification).
"""

INDUSTRIAL_AREAS = [
    {
        "id": "urla",
        "name": "Urla Industrial Area",
        "city": "Raipur",
        "center": [21.2750, 81.5650],
        "zoom": 15,
        "total_area_acres": 450,
        "established": "1985",
    },
    {
        "id": "siltara",
        "name": "Siltara Industrial Area",
        "city": "Raipur",
        "center": [21.3350, 81.5450],
        "zoom": 14,
        "total_area_acres": 2800,
        "established": "2005",
    },
    {
        "id": "borai",
        "name": "Borai Industrial Area",
        "city": "Durg",
        "center": [21.1650, 81.3050],
        "zoom": 15,
        "total_area_acres": 350,
        "established": "1990",
    },
    {
        "id": "bhilai",
        "name": "Bhilai Industrial Area",
        "city": "Durg",
        "center": [21.2100, 81.3800],
        "zoom": 15,
        "total_area_acres": 200,
        "established": "1978",
    },
    {
        "id": "korba",
        "name": "Korba Industrial Area",
        "city": "Korba",
        "center": [22.3595, 82.7501],
        "zoom": 15,
        "total_area_acres": 180,
        "established": "1992",
    },
]

# Simulated plot data for demo mode
DEMO_PLOTS = []

# Alert history for dashboard
DEMO_ALERTS = []


def get_dashboard_stats():
    """Compute dashboard KPI stats from demo data."""
    total = len(DEMO_PLOTS)
    compliant = sum(1 for p in DEMO_PLOTS if p["status"] == "compliant")
    violations = sum(1 for p in DEMO_PLOTS if p["status"] == "violation")
    vacant = sum(1 for p in DEMO_PLOTS if p["status"] == "vacant")
    pending = sum(1 for a in DEMO_ALERTS if not a["acknowledged"])

    total_allotted = sum(p["allotted_area_sqm"] for p in DEMO_PLOTS)
    total_current = sum(p["current_area_sqm"] for p in DEMO_PLOTS)
    avg_compliance = sum(p["compliance_score"] for p in DEMO_PLOTS) / total if total else 0

    # Per-area stats
    area_stats = {}
    for area in INDUSTRIAL_AREAS:
        area_plots = [p for p in DEMO_PLOTS if p["area_id"] == area["id"]]
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
    }


def get_plots_geojson(area_id=None):
    """Convert plots to GeoJSON format for map display."""
    plots = DEMO_PLOTS
    if area_id:
        plots = [p for p in plots if p["area_id"] == area_id]

    features = []
    for plot in plots:
        coords = plot["coordinates"]
        # Close the polygon
        ring = [[c[1], c[0]] for c in coords]  # GeoJSON uses [lng, lat]
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
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [ring],
            },
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}
