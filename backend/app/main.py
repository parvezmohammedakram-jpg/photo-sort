from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.schemas.base import APIResponse
from app.api.routes import projects, photos, duplicates, export
from fastapi.staticfiles import StaticFiles
from app.config import DATA_DIR

# Initialize database tables
init_db()

app = FastAPI(
    title="PhotoSort API",
    description="Automated Photo Quality Detection and Organization System",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for thumbnails and previews
app.mount("/api/files", StaticFiles(directory=str(DATA_DIR)), name="files")

# Include routes
app.include_router(projects.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(duplicates.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/api/health", response_model=APIResponse[dict])
def health_check():
    """Health check endpoint."""
    return {
        "status": "success",
        "data": {
            "service": "photosort",
            "version": "1.0.0",
            "database": "connected"
        }
    }
