# 🌍 CSIDC Land Sentinel (AI-Powered)
> **Advanced Geospatial Intelligence for Industrial Land Monitoring**

![Status](https://img.shields.io/badge/Status-Prototyping-orange)
![AI](https://img.shields.io/badge/AI-OpenCV_%2B_Gemini-blue)
![Stack](https://img.shields.io/badge/Stack-FastAPI_%2B_React_%2B_Kotlin-green)

**CSIDC Land Sentinel** is an AI-driven platform designed to automate the monitoring of industrial land allotments. It uses satellite imagery and machine learning to detect encroachments, verify land usage compliance, and generate official audit reports, replacing manual ground surveys with digital intelligence.

---

## 🏗️ System Architecture

The system follows a **Hub-and-Spoke** architecture where the Central AI Core processes data from multiple sources (Satellite, Drones, Mobile Agents) and distributes intelligence to the Dashboard and Field Officers.

```mermaid
graph TD
    subgraph "Data Sources"
        SAT[🛰️ Satellite / Drone Imagery]
        REG[📂 Official Land Registry]
        MOB[📱 Mobile Field App]
    end

    subgraph "Backend Core (FastAPI)"
        API[API Gateway]
        CV[🧠 OpenCV Image Processing]
        AI[🤖 AI Change Detection]
        DB[(Registry Database)]
    end

    subgraph "Interfaces"
        DASH[💻 Admin Dashboard (React)]
        REP[📄 PDF Report Generator]
        ALERT[🔔 Real-time Alerts]
    end

    SAT --> API
    REG --> API
    MOB -->|Field Verification| API
    
    API --> CV
    CV --> AI
    REG <--> AI
    AI --> DB
    
    DB --> DASH
    DB --> REP
    DB --> ALERT
    ALERT --> MOB
```

---

## 🚀 Key Features

### 1. **AI Change Detection Engine**
*   **Structural Analysis**: Uses edge detection (Canny) and contour analysis to compare **Approved Layouts** vs. **Satellite Imagery**.
*   **Accuracy**: Distinguishes between temporary structures and permanent encroachments.
*   **Metrics**: Calculates **Encroachment %**, **Compliance Score (0-100)**, and estimated **Financial Revenue Leakage**.

### 2. **GIS Command Center (Dashboard)**
*   **Interactive Map**: Satellite view of all industrial zones with color-coded plots (🟢 Compliant, 🔴 Violation, 🟣 Vacant).
*   **Digital Twin**: Overlays official CAD/Shapefile boundaries onto real-world maps.
*   **Audit Reports**: One-click generation of PDF compliance reports for legal notices.

### 3. **Mobile Sentinel (Android App)**
*   **Live Alerts**: Field officers receive push notifications for high-priority violations.
*   **Ground Truthing**: Officers can verify "Red Flagged" plots on-site and upload photos/status updates.
*   **Offline Mode**: Works in remote areas and syncs when connectivity is restored.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | **Python (FastAPI)** | High-performance async API, Image Processing orchestration. |
| **AI / ML** | **OpenCV, Shapely, NumPy** | Computer Vision for edge detection and geospatial geometry. |
| **Frontend** | **React.js + Vite** | Responsive Admin Dashboard with `react-leaflet` maps. |
| **Mobile** | **Kotlin (Android)** | Native Android app with Retrofit for API sync. |
| **Cloud** | **Render + Vercel** | Scalable deployment (Backend on Render, Frontend on Vercel). |
| **Tunneling**| **Ngrok** | Secure development tunneling for local-to-cloud testing. |

---

## 📂 Project Structure

```bash
📦 CSIDC-Land-Sentinel
 ┣ 📂 backend            # Python FastAPI Core
 ┃ ┣ 📜 main.py          # API Entry Point
 ┃ ┣ 📜 image_processing.py # AI & OpenCV Logic
 ┃ ┣ 📜 demo_data.py     # Mock Data for MVP
 ┃ ┗ 📜 requirements.txt # Python Dependencies
 ┣ 📂 frontend           # React Dashboard
 ┃ ┣ 📂 src/components   # UI Components (Dashboard, Maps, etc.)
 ┃ ┣ 📜 config.js        # API Connection Config
 ┃ ┗ 📜 vercel.json      # Cloud Routing
 ┣ 📂 mobile             # Android App Source
 ┃ ┗ 📂 app              # Kotlin Source Code
 ┗ 📜 render.yaml        # Backend Cloud Config
```

---

## ⚡ Deployment & Setup

### 1. Backend (Python/FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Running on: http://localhost:8000
```

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
# Running on: http://localhost:5173
```

### 3. Mobile App (Android)
*   Open `mobile/` in **Android Studio**.
*   Sync Gradle.
*   Run on Emulator or Device.

### ☁️ Cloud Deployment
*   **Backend**: Deployed on **Render.com**.
*   **Frontend**: Deployed on **Vercel**.
*   **Connectivity**: Frontend connects to Render via `config.js`.

---

## 📸 Screenshots

*(Placeholders - Add your actual screenshots here)*

| **Dashboard Analysis** | **Mobile Alerts** |
| :---: | :---: |
| ![Dashboard](https://via.placeholder.com/400x200?text=Dashboard+Screenshot) | ![Mobile](https://via.placeholder.com/200x400?text=App+Screenshot) |
| *Real-time satellite analysis & compliance scoring* | *Field officer notifications & verification* |

---

> **Hackathon Submission**: This project was built for the **Smart India Hackathon (SIH)** / **CSIDC Innovation Challenge**.
