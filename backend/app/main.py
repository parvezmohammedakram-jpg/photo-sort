from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.schemas.base import APIResponse

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

# We will mount routes here as we build them.
