"""
Demo data for CSIDC Land Sentinel MVP.
Pre-loaded industrial area coordinates and simulated plot data
from real CSIDC industrial zones in Chhattisgarh.
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
DEMO_PLOTS = [
    # Urla Industrial Area Plots
    {
        "id": "URLA-001",
        "area_id": "urla",
        "name": "M/s Raipur Steel Ltd",
        "allotted_area_sqm": 4500,
        "current_area_sqm": 4520,
        "status": "violation",
        "violation_type": "encroachment",
        "deviation_pct": 0.44,
        "compliance_score": 35,
        "lease_status": "overdue",
        "last_payment": "2025-06-15",
        "last_checked": "2026-02-10",
        "coordinates": [
            [21.2745, 81.5640],
            [21.2745, 81.5655],
            [21.2755, 81.5655],
            [21.2755, 81.5640],
        ],
    },
    {
        "id": "URLA-002",
        "area_id": "urla",
        "name": "M/s CG Polymers Pvt Ltd",
        "allotted_area_sqm": 3200,
        "current_area_sqm": 3200,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 95,
        "lease_status": "current",
        "last_payment": "2026-01-10",
        "last_checked": "2026-02-10",
        "coordinates": [
            [21.2758, 81.5640],
            [21.2758, 81.5653],
            [21.2766, 81.5653],
            [21.2766, 81.5640],
        ],
    },
    {
        "id": "URLA-003",
        "area_id": "urla",
        "name": "M/s Prasad Industries",
        "allotted_area_sqm": 5000,
        "current_area_sqm": 0,
        "status": "vacant",
        "violation_type": "unused_land",
        "deviation_pct": 100.0,
        "compliance_score": 10,
        "lease_status": "overdue",
        "last_payment": "2024-12-01",
        "last_checked": "2026-02-10",
        "coordinates": [
            [21.2740, 81.5660],
            [21.2740, 81.5678],
            [21.2750, 81.5678],
            [21.2750, 81.5660],
        ],
    },
    {
        "id": "URLA-004",
        "area_id": "urla",
        "name": "M/s National Fabricators",
        "allotted_area_sqm": 2800,
        "current_area_sqm": 3450,
        "status": "violation",
        "violation_type": "unauthorized_construction",
        "deviation_pct": 23.2,
        "compliance_score": 20,
        "lease_status": "current",
        "last_payment": "2026-01-20",
        "last_checked": "2026-02-08",
        "coordinates": [
            [21.2770, 81.5642],
            [21.2770, 81.5658],
            [21.2778, 81.5658],
            [21.2778, 81.5642],
        ],
    },
    # Siltara Industrial Area Plots
    {
        "id": "SIL-001",
        "area_id": "siltara",
        "name": "M/s Godawari Power & Ispat",
        "allotted_area_sqm": 15000,
        "current_area_sqm": 15200,
        "status": "violation",
        "violation_type": "encroachment",
        "deviation_pct": 1.3,
        "compliance_score": 55,
        "lease_status": "current",
        "last_payment": "2026-02-01",
        "last_checked": "2026-02-12",
        "coordinates": [
            [21.3340, 81.5440],
            [21.3340, 81.5470],
            [21.3360, 81.5470],
            [21.3360, 81.5440],
        ],
    },
    {
        "id": "SIL-002",
        "area_id": "siltara",
        "name": "M/s Jayaswal Neco Industries",
        "allotted_area_sqm": 12000,
        "current_area_sqm": 12000,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 98,
        "lease_status": "current",
        "last_payment": "2026-01-25",
        "last_checked": "2026-02-12",
        "coordinates": [
            [21.3362, 81.5440],
            [21.3362, 81.5465],
            [21.3378, 81.5465],
            [21.3378, 81.5440],
        ],
    },
    {
        "id": "SIL-003",
        "area_id": "siltara",
        "name": "M/s Hira Group",
        "allotted_area_sqm": 8500,
        "current_area_sqm": 8500,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 88,
        "lease_status": "current",
        "last_payment": "2026-01-15",
        "last_checked": "2026-02-11",
        "coordinates": [
            [21.3380, 81.5445],
            [21.3380, 81.5462],
            [21.3392, 81.5462],
            [21.3392, 81.5445],
        ],
    },
    {
        "id": "SIL-004",
        "area_id": "siltara",
        "name": "M/s Vandana Global Ltd",
        "allotted_area_sqm": 10000,
        "current_area_sqm": 11800,
        "status": "violation",
        "violation_type": "unauthorized_construction",
        "deviation_pct": 18.0,
        "compliance_score": 25,
        "lease_status": "overdue",
        "last_payment": "2025-08-10",
        "last_checked": "2026-02-12",
        "coordinates": [
            [21.3345, 81.5475],
            [21.3345, 81.5498],
            [21.3360, 81.5498],
            [21.3360, 81.5475],
        ],
    },
    # Borai Industrial Area Plots
    {
        "id": "BOR-001",
        "area_id": "borai",
        "name": "M/s Chhattisgarh Steel",
        "allotted_area_sqm": 6000,
        "current_area_sqm": 6000,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 92,
        "lease_status": "current",
        "last_payment": "2026-02-05",
        "last_checked": "2026-02-09",
        "coordinates": [
            [21.1645, 81.3040],
            [21.1645, 81.3058],
            [21.1655, 81.3058],
            [21.1655, 81.3040],
        ],
    },
    {
        "id": "BOR-002",
        "area_id": "borai",
        "name": "M/s Durg Alloys Ltd",
        "allotted_area_sqm": 4000,
        "current_area_sqm": 4800,
        "status": "violation",
        "violation_type": "encroachment",
        "deviation_pct": 20.0,
        "compliance_score": 30,
        "lease_status": "overdue",
        "last_payment": "2025-04-20",
        "last_checked": "2026-02-09",
        "coordinates": [
            [21.1657, 81.3042],
            [21.1657, 81.3055],
            [21.1665, 81.3055],
            [21.1665, 81.3042],
        ],
    },
    {
        "id": "BOR-003",
        "area_id": "borai",
        "name": "M/s Green Energy Solutions",
        "allotted_area_sqm": 3500,
        "current_area_sqm": 0,
        "status": "vacant",
        "violation_type": "unused_land",
        "deviation_pct": 100.0,
        "compliance_score": 5,
        "lease_status": "overdue",
        "last_payment": "2024-06-01",
        "last_checked": "2026-02-09",
        "coordinates": [
            [21.1640, 81.3062],
            [21.1640, 81.3075],
            [21.1648, 81.3075],
            [21.1648, 81.3062],
        ],
    },
    # Bhilai
    {
        "id": "BHI-001",
        "area_id": "bhilai",
        "name": "M/s Bhilai Engineering Corp",
        "allotted_area_sqm": 7000,
        "current_area_sqm": 7000,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 90,
        "lease_status": "current",
        "last_payment": "2026-01-30",
        "last_checked": "2026-02-07",
        "coordinates": [
            [21.2095, 81.3790],
            [21.2095, 81.3812],
            [21.2108, 81.3812],
            [21.2108, 81.3790],
        ],
    },
    {
        "id": "BHI-002",
        "area_id": "bhilai",
        "name": "M/s Shri Cement Industries",
        "allotted_area_sqm": 5500,
        "current_area_sqm": 6700,
        "status": "violation",
        "violation_type": "encroachment",
        "deviation_pct": 21.8,
        "compliance_score": 28,
        "lease_status": "overdue",
        "last_payment": "2025-09-15",
        "last_checked": "2026-02-07",
        "coordinates": [
            [21.2110, 81.3792],
            [21.2110, 81.3808],
            [21.2120, 81.3808],
            [21.2120, 81.3792],
        ],
    },
    # Korba
    {
        "id": "KOR-001",
        "area_id": "korba",
        "name": "M/s Korba Thermal Power",
        "allotted_area_sqm": 20000,
        "current_area_sqm": 20000,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 97,
        "lease_status": "current",
        "last_payment": "2026-02-01",
        "last_checked": "2026-02-06",
        "coordinates": [
            [22.3585, 82.7490],
            [22.3585, 82.7515],
            [22.3605, 82.7515],
            [22.3605, 82.7490],
        ],
    },
    {
        "id": "KOR-002",
        "area_id": "korba",
        "name": "M/s CG Mining Solutions",
        "allotted_area_sqm": 9000,
        "current_area_sqm": 9000,
        "status": "compliant",
        "violation_type": None,
        "deviation_pct": 0.0,
        "compliance_score": 85,
        "lease_status": "current",
        "last_payment": "2026-01-28",
        "last_checked": "2026-02-06",
        "coordinates": [
            [22.3607, 82.7492],
            [22.3607, 82.7510],
            [22.3618, 82.7510],
            [22.3618, 82.7492],
        ],
    },
]

# Alert history for dashboard
DEMO_ALERTS = [
    {
        "id": 1,
        "plot_id": "URLA-004",
        "type": "unauthorized_construction",
        "severity": "critical",
        "message": "Unauthorized construction detected beyond plot boundary — 23.2% deviation",
        "timestamp": "2026-02-08T14:30:00",
        "area": "Urla Industrial Area",
        "acknowledged": False,
    },
    {
        "id": 2,
        "plot_id": "SIL-004",
        "type": "unauthorized_construction",
        "severity": "critical",
        "message": "Major unauthorized expansion detected — 18% deviation from allotted boundary",
        "timestamp": "2026-02-12T09:15:00",
        "area": "Siltara Industrial Area",
        "acknowledged": False,
    },
    {
        "id": 3,
        "plot_id": "URLA-003",
        "type": "unused_land",
        "severity": "warning",
        "message": "Plot remains vacant despite allotment — no construction activity detected",
        "timestamp": "2026-02-10T11:00:00",
        "area": "Urla Industrial Area",
        "acknowledged": True,
    },
    {
        "id": 4,
        "plot_id": "BOR-002",
        "type": "encroachment",
        "severity": "critical",
        "message": "Encroachment beyond allotted boundary — 20% area deviation detected",
        "timestamp": "2026-02-09T16:45:00",
        "area": "Borai Industrial Area",
        "acknowledged": False,
    },
    {
        "id": 5,
        "plot_id": "BHI-002",
        "type": "encroachment",
        "severity": "critical",
        "message": "Boundary encroachment detected — 21.8% excess area usage",
        "timestamp": "2026-02-07T10:20:00",
        "area": "Bhilai Industrial Area",
        "acknowledged": True,
    },
    {
        "id": 6,
        "plot_id": "BOR-003",
        "type": "unused_land",
        "severity": "warning",
        "message": "Allotted land remains completely unused — lease payments overdue since June 2024",
        "timestamp": "2026-02-09T08:30:00",
        "area": "Borai Industrial Area",
        "acknowledged": False,
    },
    {
        "id": 7,
        "plot_id": "URLA-001",
        "type": "encroachment",
        "severity": "moderate",
        "message": "Minor boundary deviation detected — 0.44% encroachment noted",
        "timestamp": "2026-02-10T13:10:00",
        "area": "Urla Industrial Area",
        "acknowledged": True,
    },
    {
        "id": 8,
        "plot_id": "SIL-001",
        "type": "encroachment",
        "severity": "moderate",
        "message": "Slight boundary deviation — 1.3% excess area beyond allotted plot",
        "timestamp": "2026-02-12T07:45:00",
        "area": "Siltara Industrial Area",
        "acknowledged": False,
    },
]


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
