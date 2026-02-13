"""
Core Reporting Engine: Visualization, Audit Logs, & Compliance Dashboard Data.
"""

import json
import os
from datetime import datetime

class ReportingEngine:
    def __init__(self, results_dir):
        self.results_dir = results_dir

    def generate_audit_report(self, project_id: str, intelligence_data: dict, compliance_data: dict, economic_data: dict) -> dict:
        """
        PHASE 12: Visual & Reporting Output.
        Generates structured, audit-ready JSON report.
        """
        report = {
            "report_id": f"RPT-{project_id}-{int(datetime.now().timestamp())}",
            "generated_at": datetime.now().isoformat(),
            "project_id": project_id,
            "intelligence": {
                "plot_id": intelligence_data.get("plot_id", "UNKNOWN"),
                "coordinates": intelligence_data.get("coordinates", {}),
                "total_plot_area_sqft": intelligence_data.get("area_sqft", 0),
            },
            "compliance": {
                "status": compliance_data.get("classification", "Unknown"),
                "risk_level": compliance_data.get("risk", {}).get("level", "UNKNOWN"),
                "encroachment_pct": compliance_data.get("encroachment_pct", 0),
                "utilization_pct": compliance_data.get("utilization_pct", 0),
                "recommended_actions": compliance_data.get("actions", [])
            },
            "economics": {
                "estimated_revenue_loss": economic_data.get("estimated_revenue_leakage", 0),
                "recoverable_penalty": economic_data.get("recoverable_penalty", 0),
                "industrial_health_index": economic_data.get("health_index", 0)
            },
            "audit_trail": {
                "version": "2.0 (Core Engine)",
                "verified_by": "Automated System",
                "hash": hash(str(compliance_data)) # Simple hash for integrity
            }
        }
        
        # Save to disk
        report_path = os.path.join(self.results_dir, project_id, "audit_report.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report
