# 🛰️ CSIDC Land Sentinel
**Advanced Industrial Land Intelligence & Financial Compliance System**

An AI-powered satellite monitoring platform that automates boundary compliance, legal risk assessment, and financial revenue maximization for industrial allotments.

![Dashboard](https://via.placeholder.com/800x400?text=CSIDC+Land+Sentinel+Dashboard)

## 🚀 Key Innovations (12-Phase System)

### 🧠 Phase 1-4: Advanced Intelligence Engine
- **Raster-to-Vector**: Reconstructs digital plot boundaries from static maps using HSV segmentation and contour approximation.
- **OCR Integration**: Extracts plot IDs from map scans (Stubbed/Designed).
- **Georeferencing**: Maps pixel coordinates to real-world Lat/Long.
- **Satellite Analysis**: Detects built-up structures using adaptive thresholding and morphological filtering.

### ⚖️ Phase 5-7: Compliance & Risk Engine
- **True Encroachment Logic**: `Violation = Built-up Area AND (NOT Approved Boundary)`.
- **Strict ROI Alignment**: Auto-crops images to approved bounding boxes to prevent false positives.
- **Smart Classification**: Auto-labels land as *Vacant*, *Under Construction*, *Fully Constructed*, or *Encroached*.
- **Risk Scoring**: Assigns `CRITICAL`, `MAJOR`, `MODERATE`, or `LOW` risk severity based on % deviation.

### 💰 Phase 8-10: Economics & Health Engine
- **Financial Impact Estimator**: Calculates `Estimated Revenue Leakage` (from vacancy) and `Recoverable Penalties` (from encroachment).
- **Industrial Health Index**: A composite score (0-100) tracking utilization efficiency and compliance.

### 📋 Phase 11-12: Governance & Reporting
- **Decision Support**: Automated administrative recommendations (e.g., "Issue Notice", "Legal Escalation").
- **Audit Trails**: One-click download of immutable JSON audit logs.

## 🛠️ Tech Stack
- **Core**: Python 3.10+, FastAPI
- **Computer Vision**: OpenCV (Structural Analysis, HSV, Contours)
- **Frontend**: React 18, Vite, Recharts, Leaflet Maps
- **Architecture**: Modular Core (`backend/core/`) + Service Orchestrator

## 🚀 Quick Start

### 1. Backend
```bash
cd backend
# Install dependencies (ensure cv2, numpy, fastapi, uvicorn are present)
pip install -r requirements.txt
# Run the Advanced Intelligence Server
python -m uvicorn main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Access at [http://localhost:5173](http://localhost:5173)

## 👥 Hackathon Team
Built for **CSIDC Automated Industrial Land Monitoring**.
*Redefining Governance with Satellite Intelligence.*
