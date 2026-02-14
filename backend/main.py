"""
CSIDC Land Sentinel — FastAPI Backend
Automated Monitoring and Compliance of Industrial Land Allotments
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import router
from admin_routes import router as admin_router
from citizen_routes import router as citizen_router

app = FastAPI(
    title="CSIDC Land Sentinel API",
    description="Automated land monitoring system for industrial allotments",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving result images
results_dir = os.path.join(os.path.dirname(__file__), "results")
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(results_dir, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/results", StaticFiles(directory=results_dir), name="results")
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Register API routes
app.include_router(router)
app.include_router(admin_router)
app.include_router(citizen_router)


@app.get("/")
async def root():
    return {
        "name": "CSIDC Land Sentinel API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
