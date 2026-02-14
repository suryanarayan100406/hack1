# 🌍 CSIDC Land Sentinel (AI-Powered)
> **Advanced Geospatial Intelligence for Industrial Land Monitoring**

![Status](https://img.shields.io/badge/Status-Live_Cloud_Demo-orange)
![AI](https://img.shields.io/badge/AI-OpenCV_%2B_Gemini-blue)
![Stack](https://img.shields.io/badge/Stack-FastAPI_%2B_React_%2B_Kotlin-green)
![License](https://img.shields.io/badge/License-MIT-purple)

**CSIDC Land Sentinel** is an AI-driven platform designed to automate the monitoring of industrial land allotments. It uses satellite imagery and machine learning to detect encroachments, verify land usage compliance, and generate official audit reports, replacing manual ground surveys with digital intelligence.

---

## 🏗️ System Architecture

The system follows a **Split-Cloud** architecture where the Central AI Core (Python/Render) processes data from multiple sources and distributes intelligence to the Dashboard (Netlify/Vercel) and Field Officers (Android).

```mermaid
graph TD
    subgraph "Data Sources"
        SAT[🛰️ Satellite / Drone Imagery]
        REG[📂 Official Land Registry]
        CIT[👁️ Citizen Reports]
    end

    subgraph "Backend Core (Render.com)"
        API[API Gateway (FastAPI)]
        CV[🧠 OpenCV Image Processing]
        AI[🤖 AI Change Detection]
        DB[(Registry Database)]
    end

    subgraph "Interfaces"
        DASH[💻 Admin Dashboard (React/Netlify)]
        REP[📄 PDF Report Generator]
        MOB[📱 Mobile Field App (Android)]
        PUB[📢 Public Reporting Portal]
    end

    SAT --> API
    REG --> API
    CIT --> API
    
    API --> CV
    CV --> AI
    REG <--> AI
    AI --> DB
    
    DB --> DASH
    DB --> REP
    DB --> MOB
    DASH <--> MOB
    MOB -->|Field Verification| API
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
*   **Live Notifications**: Field officers receive **Real-time Push Notifications** for high-priority violations (Severity > 70%).
*   **Ground Truthing**: Officers verify "Red Flagged" plots on-site.
*   **Cloud Sync**: Connected to live Render backend for up-to-the-minute data.

### 4. **Citizen Watch Portal (New!)**
*   **Public Reporting**: Citizens can pin GPS locations and upload photos of potential encroachments.
*   **Transparency**: View recent reports on a public map.
*   **Vigilance**: Crowdsourced data feeds directly into the Admin Dashboard.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | **Python (FastAPI)** | Hosted on **Render.com**. Handles AI logic & Image Processing. |
| **AI / ML** | **OpenCV, Shapely, NumPy** | Computer Vision for edge detection and geospatial geometry. |
| **Frontend** | **React.js + Vite** | Hosted on **Netlify/Vercel**. Admin Dashboard & Citizen Portal. |
| **Mobile** | **Kotlin (Android)** | Native Android app with Retrofit & Notification Services. |
| **Database** | **JSON/File System** | Persistent storage on Render disk (MVP). |

---

## 📂 Project Structure

```bash
📦 CSIDC-Land-Sentinel
 ┣ 📂 backend            # Python FastAPI Core (Render)
 ┃ ┣ 📜 main.py          # API Entry Point
 ┃ ┣ 📜 image_processing.py # AI & OpenCV Logic
 ┃ ┣ 📜 citizen_routes.py # Public Reporting API
 ┃ ┣ 📜 Procfile         # Render Ecosystem Config
 ┃ ┗ 📜 requirements.txt # Python Dependencies
 ┣ 📂 frontend           # React Dashboard (Netlify/Vercel)
 ┃ ┣ 📂 src/components   # Dashboard, Maps, Citizen Watch
 ┃ ┣ 📜 config.js        # API Connection Config (Env Vars)
 ┃ ┗ 📜 vercel.json      # Cloud Routing
 ┣ 📂 mobile             # Android App Source
 ┃ ┗ 📂 app              # Kotlin Source Code
 ┗ 📜 DEPLOYMENT_GUIDE.md # Full Cloud Setup Instructions
```

---

## ⚡ Deployment & Setup

### ☁️ Cloud Deployment (Live)
*   **Backend**: Deployed on **Render.com** (Web Service, Python 3.10).
    *   *Start Command*: `cd backend && gunicorn main:app -k uvicorn.workers.UvicornWorker`
*   **Frontend**: Deployed on **Netlify / Vercel**.
    *   *Env Var*: `VITE_API_BASE_URL` = `https://your-render-backend.onrender.com`

### 💻 Local Development
1.  **Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    python -m uvicorn main:app --reload
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

### 📱 Mobile App
*   Open `mobile/` in **Android Studio**.
*   **Sync Gradle** & Run on Device.
*   *Note: Notifications require Android 13+ permission approval.*

---

## 📸 Screenshots

*(Placeholders - Add your actual screenshots here)*

| **Dashboard Analysis** | **Mobile Notifications** | **Citizen Portal** |
| :---: | :---: | :---: |
| ![Dashboard](https://via.placeholder.com/300x200?text=Dashboard) | ![Mobile](https://via.placeholder.com/150x300?text=App+Alert) | ![Citizen](https://via.placeholder.com/300x200?text=Public+Report) |
| *Satellite Analysis* | *Real-time Alerts* | *Public Reporting* |

---

> **Hackathon Submission**: This project was built for the **Smart India Hackathon (SIH)** / **CSIDC Innovation Challenge**.
