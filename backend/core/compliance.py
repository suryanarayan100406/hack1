"""
Core Compliance Engine: Encroachment Logic, Land Classification, & Legal Risk Scoring.
"""

import cv2
import numpy as np

class ComplianceEngine:
    def __init__(self):
        # Risk Thresholds
        self.risk_levels = {
            "critical": 30.0,  # > 30% encroachment
            "major": 15.0,     # > 15%
            "moderate": 5.0,   # > 5%
            "low": 0.0         # > 0%
        }

    def compute_encroachment(self, plot_mask: np.ndarray, built_up_mask: np.ndarray) -> dict:
        """
        PHASE 5: True Encroachment Logic.
        Encroachment = Built-up Area OUTSIDE Approved Plot Polygon.
        Returns metrics and binary masks.
        """
        # Ensure sizes match
        if plot_mask.shape != built_up_mask.shape:
            raise ValueError("Mask dimensions mismatch")
            
        # 1. Define 'Outside' Zone = NOT Plot Mask
        outside_zone = cv2.bitwise_not(plot_mask)
        
        # 2. Encroachment = Built Up AND Outside Zone
        encroachment_mask = cv2.bitwise_and(built_up_mask, outside_zone)
        
        # 3. Clean noise (Optional step if not done in intelligence)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        encroachment_mask = cv2.morphologyEx(encroachment_mask, cv2.MORPH_OPEN, kernel)
        
        # 4. Metrics
        approved_px = cv2.countNonZero(plot_mask)
        built_inside_px = cv2.countNonZero(cv2.bitwise_and(built_up_mask, plot_mask))
        encroached_px = cv2.countNonZero(encroachment_mask)
        
        if approved_px < 1: approved_px = 1 # Avoid Div/0
        
        # Clamp Logic (Safety)
        if encroached_px > approved_px:
             encroached_px = approved_px
             
        encroachment_pct = (encroached_px / approved_px) * 100.0
        utilization_pct = (built_inside_px / approved_px) * 100.0
        
        return {
            "encroachment_pct": round(encroachment_pct, 2),
            "utilization_pct": round(utilization_pct, 2),
            "approved_px": int(approved_px),
            "encroached_px": int(encroached_px),
            "built_inside_px": int(built_inside_px),
            "masks": {
                "encroachment": encroachment_mask,
                "built_inside": cv2.bitwise_and(built_up_mask, plot_mask)
            }
        }

    def classify_land(self, metrics: dict) -> str:
        """
        PHASE 6: Smart Land Classification.
        Determines the state of the plot.
        """
        encr = metrics["encroachment_pct"]
        util = metrics["utilization_pct"]
        
        if encr > 10.0:
            return "Major Encroachment"
        elif encr > 1.0:
            return "Encroached"
        elif util < 5.0:
            return "Vacant"
        elif util < 30.0:
            return "Under Construction" # Or 'Partially Developed'
        elif util >= 30.0:
            return "Fully Constructed"
        else:
            return "Unknown"

    def calculate_risk_score(self, encroachment_pct: float) -> dict:
        """
        PHASE 7: Legal Risk Scoring Engine.
        """
        if encroachment_pct >= self.risk_levels["critical"]:
            return {"level": "CRITICAL", "score": 100, "color": "red"}
        elif encroachment_pct >= self.risk_levels["major"]:
             return {"level": "MAJOR VIOLATION", "score": 75, "color": "orange"}
        elif encroachment_pct >= self.risk_levels["moderate"]:
             return {"level": "MODERATE RISK", "score": 40, "color": "yellow"}
        elif encroachment_pct > 0.5:
             return {"level": "LOW RISK", "score": 10, "color": "blue"}
        else:
             return {"level": "COMPLIANT", "score": 0, "color": "green"}

    def recommend_actions(self, risk_data: dict, classification: str) -> list:
        """
        PHASE 11: Administrative Decision Engine.
        Returns actionable steps for officials.
        """
        actions = []
        level = risk_data["level"]
        
        if level == "CRITICAL":
            actions.append("Issue Immediate Stop-Work Notice")
            actions.append("Schedule Field Inspection (High Priority)")
            actions.append("Legal Escalation for Demolition")
        elif level == "MAJOR VIOLATION":
            actions.append("Issue Warning Notice")
            actions.append("Schedule Field Inspection")
            actions.append("Review Lease Agreement Conditions")
        elif level == "MODERATE RISK":
            actions.append("Notify Allottee to Rectify Boundary")
            actions.append("Monitor via Satellite Next Cycle")
        elif level == "LOW RISK":
            actions.append("Monitor Only")
            
        if classification == "Vacant":
             actions.append("Check Non-Utilization Penalty Applicability")
             
        return actions
