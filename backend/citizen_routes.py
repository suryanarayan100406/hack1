from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import os
import shutil

router = APIRouter(prefix="/api/citizen", tags=["citizen"])

# In-memory storage for MVP (would be DB in prod)
PUBLIC_REPORTS = []

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "citizen")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ReportResponse(BaseModel):
    id: str
    lat: float
    lng: float
    description: str
    status: str
    timestamp: str
    image_url: Optional[str] = None

@router.get("/reports", response_model=List[ReportResponse])
async def get_public_reports():
    """Get all public reports."""
    # Return dummy data if empty
    if not PUBLIC_REPORTS:
        return [
            {
                "id": "REP-001",
                "lat": 21.2800,
                "lng": 81.5700,
                "description": "Illegal dumping near Plot 42",
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
                "image_url": None
            }
        ]
    return PUBLIC_REPORTS

@router.post("/report")
async def submit_report(
    description: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    file: UploadFile = File(None)
):
    """Submit a new public report."""
    report_id = f"REP-{int(datetime.now().timestamp())}"
    
    image_url = None
    if file:
        filename = f"{report_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)
        image_url = f"/uploads/citizen/{filename}"

    report = {
        "id": report_id,
        "lat": lat,
        "lng": lng,
        "description": description,
        "status": "pending",
        "timestamp": datetime.now().isoformat(),
        "image_url": image_url
    }
    
    PUBLIC_REPORTS.append(report)
    
    return {
        "status": "success",
        "message": "Report submitted successfully",
        "report_id": report_id
    }
