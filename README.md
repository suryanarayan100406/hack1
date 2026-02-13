# 🛰️ CSIDC Land Sentinel

**Automated Monitoring and Compliance of Industrial Land Allotments for Financial Efficiency**

An AI-powered satellite monitoring system that enables CSIDC to detect boundary violations, encroachments, and unauthorized construction on industrial land parcels — reducing reliance on expensive drone surveys.

## ✨ Key Features

- **📊 Dashboard** — Real-time KPI cards, area-wise compliance charts, and alert feeds
- **🗺️ Interactive Map** — Leaflet-based satellite map with GeoJSON plot boundary overlays (ESRI satellite tiles)
- **📤 Upload & Analyze** — Drag-drop upload of reference maps + satellite images for automated change detection
- **🔍 Change Detection** — OpenCV-powered pixel-diff analysis with heatmaps, contour detection, and annotated overlays
- **📋 Compliance Reports** — Filterable table with compliance scores, CSV export, and per-plot status
- **🔔 Alert System** — Severity-based violation alerts with acknowledge/dismiss workflow
- **🎯 Demo Mode** — Pre-loaded CSIDC industrial areas (Urla, Siltara, Borai, Bhilai, Korba) with real coordinates

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, React-Leaflet, Recharts |
| Backend | Python 3, FastAPI, OpenCV, NumPy, Pillow |
| Maps | Leaflet + ESRI World Imagery + OpenStreetMap |
| Design | Dark glassmorphism CSS, Inter font, responsive |

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## 📁 Project Structure

```
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routes.py               # API endpoints
│   ├── image_processing.py     # OpenCV change detection engine
│   ├── demo_data.py            # Pre-loaded CSIDC industrial area data
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Root component with page routing
│   │   ├── index.css           # Full design system (dark glassmorphism)
│   │   ├── components/
│   │   │   ├── Dashboard.jsx   # KPI cards, charts, alerts feed
│   │   │   ├── MapView.jsx     # Interactive Leaflet map with GeoJSON overlays
│   │   │   ├── Upload.jsx      # Drag-drop image upload + analysis trigger
│   │   │   ├── Analysis.jsx    # Change detection results viewer
│   │   │   ├── Reports.jsx     # Compliance report table with CSV export
│   │   │   ├── Alerts.jsx      # Alert feed with severity filtering
│   │   │   └── Sidebar.jsx     # Navigation sidebar
│   │   └── main.jsx            # React entry point
│   ├── index.html              # HTML entry with fonts
│   ├── vite.config.js          # Vite + API proxy config
│   └── package.json            # NPM dependencies
└── .gitignore
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/demo-data` | All demo data for dashboard |
| GET | `/api/stats` | Dashboard KPI statistics |
| GET | `/api/areas` | List all industrial areas |
| GET | `/api/plots` | List all plots (filterable) |
| GET | `/api/geojson` | Plots as GeoJSON for map |
| GET | `/api/alerts` | All violation alerts |
| POST | `/api/upload` | Upload reference + satellite images |
| POST | `/api/analyze/{id}` | Run change detection on project |
| GET | `/api/projects` | List analysis projects |

## 🎯 How It Works

1. **Upload** — Officials upload the original allotment map (reference) and a recent satellite/drone image
2. **AI Analysis** — OpenCV aligns images, computes pixel-level differences, detects contour boundaries
3. **Results** — System generates heatmaps, annotated overlays, compliance scores, and deviation reports
4. **Monitor** — Dashboard shows real-time status across all industrial areas with actionable alerts

## 👥 Team

Built for the CSIDC Hackathon — Automated Industrial Land Monitoring
