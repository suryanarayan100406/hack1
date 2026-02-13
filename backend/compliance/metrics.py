"""
PHASE 4: POLYGON-BASED ENCROACHMENT ANALYSIS
Uses Shapely geometry operations to compute accurate encroachment areas and compliance status.
"""

from shapely.geometry import Polygon
from typing import List, Dict

def calculate_encroachment(layout_poly: Polygon, builtup_polys: List[Polygon]):
    """
    Compute encroachment metrics using boolean polygon operations.
    
    Args:
        layout_poly: The approved plot boundary (Shapely Polygon).
        builtup_polys: List of detected built-up structures (Shapely Polygons).
        
    Returns:
        metrics: Dictionary containing area stats and encroachment details.
    """
    total_approved_area = layout_poly.area
    total_builtup_area = 0.0
    total_encroached_area = 0.0
    encroachment_polys = [] # Polygons representing violations

    if total_approved_area == 0:
        return {
            "approved_area": 0,
            "builtup_area": 0,
            "encroached_area": 0,
            "encroachment_pct": 0,
            "status": "INVALID_LAYOUT"
        }

    for poly in builtup_polys:
        # Calculate intersection (Valid construction)
        intersection = poly.intersection(layout_poly)
        valid_area = intersection.area
        
        # Calculate difference (Encroachment)
        # encroachment = poly - layout
        difference = poly.difference(layout_poly)
        
        if not difference.is_empty:
            encroachment_polys.append(difference)
            total_encroached_area += difference.area
            
        total_builtup_area += poly.area

    # Encroachment Percentage relative to Approved Area
    raw_pct = (total_encroached_area / total_approved_area) * 100
    encroachment_pct = min(raw_pct, 100.0) # Cap at 100% as per user requirement
    
    # Cap at 100% just in case, though theoretically possible to be >100% if huge
    # User requirement from earlier: "Ensure encroachment area cannot exceed boundary"
    # But in GIS logic, if I build outside, it IS outside. 
    # The percentage is "Encroached Area / Approved Area".
    
    return {
        "approved_area": total_approved_area,
        "builtup_area": total_builtup_area,
        "encroached_area": total_encroached_area,
        "encroachment_pct": encroachment_pct,
        "encroachment_polygons": encroachment_polys # For visualization
    }

def calculate_health_index(metrics: Dict) -> float:
    """
    Phase 5: Industrial Health Index (0-100)
    Based on Utilization and Encroachment.
    """
    utilization_pct = (metrics["builtup_area"] / metrics["approved_area"]) * 100
    encroachment_pct = metrics["encroachment_pct"]
    
    # Base score
    score = 100.0
    
    # Penalize Encroachment heavily
    score -= (encroachment_pct * 2.5) 
    
    # Penalize Under-utilization (if < 30%)
    if utilization_pct < 30:
        score -= (30 - utilization_pct) * 0.5
        
    return max(0.0, min(100.0, score))

def determine_classification(metrics: Dict) -> str:
    """Phase 5: Land Classification Engine."""
    utilization_pct = (metrics["builtup_area"] / metrics["approved_area"]) * 100
    encroachment_pct = metrics["encroachment_pct"]
    
    if encroachment_pct > 15:
        return "MAJOR_VIOLATION"
    if encroachment_pct > 0.5:
        return "ENCROACHMENT_MINOR"
        
    if utilization_pct < 5:
        return "VACANT"
    if utilization_pct < 40:
        return "UNDER_CONSTRUCTION"
        
    return "FULLY_CONSTRUCTED"

def recommend_actions(classification: str, health_index: float) -> List[str]:
    """Phase 5.5: Governance Actions."""
    actions = []
    
    if "VIOLATION" in classification or "ENCROACHMENT" in classification:
        actions.append("Issue Notice under Section 24")
        actions.append("Schedule Site Inspection")
        if health_index < 40:
            actions.append("Escalate to Legal Cell")
            
    if classification == "VACANT":
        actions.append("Verify Lease Utilization Terms")
        actions.append("Send Reminder for Construction Check")
        
    if classification == "FULLY_CONSTRUCTED" and health_index > 80:
        actions.append("Compliance Verified - No Action Needed")
        
    if not actions:
        actions.append("Monitor via Satellite (Next Cycle)")
        
    return actions
