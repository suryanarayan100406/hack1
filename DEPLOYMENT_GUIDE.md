# 🚀 Final Deployment Guide

This guide explains how to deploy your "Hub-and-Spoke" architecture to the cloud and connect everything.

---

## 🏗️ 1. Backend (The Brain)
**Recommended Host: Render.com**
> *Why not Vercel?* Vercel has a 250MB size limit (which OpenCV exceeds) and does not allow file uploads (your specific requirement).*

1.  **Push code to GitHub**.
2.  Go to [dashboard.render.com](https://dashboard.render.com).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub Repository.
5.  **Important Settings**:
    *   **Root Directory**: `backend` (Leave empty if `render.yaml` handles it, but safer to specify if doing manual).
    *   **Runtime**: Python 3.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn main:app -k uvicorn.workers.UvicornWorker`
6.  Click **Deploy**.
7.  **Copy the URL**: You will get something like `https://land-sentinel.onrender.com`.

---

## 💻 2. Frontend (The Dashboard)
**Host: Netlify**

1.  Go to [app.netlify.com](https://app.netlify.com).
2.  **Add New Site** -> **Import from Git** -> **GitHub**.
3.  Select your Repository.
4.  **Build Settings**:
    *   **Base Directory**: `frontend`
    *   **Build Command**: `npm run build`
    *   **Publish Directory**: `frontend/dist` or `dist`
5.  **Environment Variables** (Crucial Step):
    *   Click **"Add Environment Variable"**.
    *   Key: `VITE_API_BASE_URL`
    *   Value: `https://land-sentinel.onrender.com` (Your Render URL from Step 1).
6.  Click **Deploy Site**.

---

## 📱 3. Mobile App (The Sentinel)
**Device: Android**

1.  Open Project in **Android Studio**.
2.  Open `app/src/main/java/com/example/landsentinel/MainActivity.kt`.
3.  Find the line with `baseUrl`:
    ```kotlin
    .baseUrl("http://10.0.2.2:8000") // OLD (Localhost)
    ```
4.  Replace it with your Render URL:
    ```kotlin
    .baseUrl("https://land-sentinel.onrender.com") // NEW (Cloud)
    ```
5.  **Build** -> **Build Bundle(s) / APK(s)** -> **Build APK**.
6.  Transfer `.apk` to your phone and install.

---

## 🔗 How it Connects
*   **Frontend** talks to **Render Backend** via the URL set in Netlify Environment Variables.
*   **Android App** talks to **Render Backend** via the URL hardcoded in `MainActivity.kt`.
*   **Render Backend** processes everything.

**✅ Setup Complete!**
