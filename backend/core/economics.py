"""
Core Economics Engine: Financial Impact, Revenue Estimation, & Industrial Health Index.
"""

class EconomicsEngine:
    def __init__(self):
        # Base Rates (configurable)
        self.lease_rate_per_sqft = 50.0  # Annual Lease Rate (INR/USD)
        self.penalty_rate_per_sqft = 200.0 # Penalty for encroachment
        self.vacancy_loss_factor = 1.0   # 100% loss if vacant

    def estimate_financial_impact(self, plot_area_sqft: float, metrics: dict, classification: str) -> dict:
        """
        PHASE 8: Financial Impact Estimator.
        Estimates revenue loss due to vacancy or potential revenue from penalties.
        """
        encroached_px = metrics["encroached_px"]
        approved_px = metrics["approved_px"]
        
        # Area conversion (Assuming scale provided, else ratio)
        # If plot_area_sqft is known, we map pixels to sqft
        px_to_sqft = plot_area_sqft / approved_px if approved_px > 0 else 0
        
        encroached_sqft = encroached_px * px_to_sqft
        
        # 1. Revenue Loss (Vacancy)
        potential_revenue = plot_area_sqft * self.lease_rate_per_sqft
        actual_revenue = 0 if classification == "Vacant" else potential_revenue
        revenue_leakage = potential_revenue - actual_revenue
        
        # 2. Penalty Recovery Potential (Encroachment)
        potential_penalty = encroached_sqft * self.penalty_rate_per_sqft
        
        return {
            "potential_annual_revenue": round(potential_revenue, 2),
            "estimated_revenue_leakage": round(revenue_leakage, 2),
            "recoverable_penalty": round(potential_penalty, 2),
            "inefficiency_index": round((revenue_leakage / potential_revenue) * 100, 1) if potential_revenue > 0 else 0
        }

    def calculate_health_index(self, metrics: dict, risk_score: int) -> float:
        """
        PHASE 9: Industrial Health Index (0-100).
        Composite Score of Utilization, Compliance, and Risk.
        Higher is Better.
        """
        utilization = metrics["utilization_pct"] # 0-100
        compliance = 100.0 - metrics["encroachment_pct"] # 0-100
        risk_penalty = risk_score # 0-100 (Critical=100)
        
        # Formula:
        # Health = (Utilization * 0.4) + (Compliance * 0.4) - (Risk * 0.2)
        health = (utilization * 0.4) + (compliance * 0.4) - (risk_penalty * 0.2)
        
        return max(0.0, min(100.0, float(health)))

    def project_trends(self, historical_data: list) -> dict:
        """
        PHASE 10: Time-Series Monitoring.
        Analyzes trend from history.
        """
        if not historical_data:
            return {"trend": "stable", "growth_rate": 0.0}
            
        # Linear regression slope for encroachment %
        # checking last 5 points
        pass # Placeholder for MVP
