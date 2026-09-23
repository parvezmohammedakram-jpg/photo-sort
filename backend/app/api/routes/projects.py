from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectProcessingStatus
from app.schemas.base import APIResponse
from app.models.project import Project
from app.services.ingestion import create_project
from app.services.pipeline import run_analysis_pipeline
from app.config import DATA_DIR

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=APIResponse[ProjectResponse])
def create_new_project(
    project_in: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new project by specifying a directory path.
    This discovers files and initializes database records.
    """
    try:
        project = create_project(db, name=project_in.name, source_path=project_in.source_path)
        
        # Trigger the background analysis pipeline
        background_tasks.add_task(run_analysis_pipeline, project.id)
        
        return {
            "status": "success",
            "data": project
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.post("/upload", response_model=APIResponse[ProjectResponse])
async def upload_new_project(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Create a new project by uploading files directly.
    Files will be stored in an internal directory before processing.
    """
    try:
        # Create a unique directory for this upload
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_dir = DATA_DIR / "uploads" / f"{name}_{timestamp}"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save all uploaded files to the directory
        for file in files:
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
        # Now create the project using this internal directory
        project = create_project(db, name=name, source_path=str(upload_dir))
        
        # Trigger the background analysis pipeline
        background_tasks.add_task(run_analysis_pipeline, project.id)
        
        return {
            "status": "success",
            "data": project
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")

@router.get("", response_model=APIResponse[List[ProjectResponse]])
def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return {
        "status": "success",
        "data": projects
    }

@router.get("/{project_id}", response_model=APIResponse[ProjectResponse])
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return {
        "status": "success",
        "data": project
    }

@router.get("/{project_id}/status", response_model=APIResponse[ProjectProcessingStatus])
def get_project_status(project_id: int, db: Session = Depends(get_db)):
    """Get the processing status of a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Calculate progress
    total = project.supported_files
    if total == 0:
        percent = 0.0
    else:
        percent = ((project.processed_files + project.failed_files) / total) * 100
        
    return {
        "status": "success",
        "data": {
            "project_id": project.id,
            "project_status": project.status,
            "total": total,
            "processed": project.processed_files,
            "failed": project.failed_files,
            "progress_percent": round(percent, 1),
            "created_at": project.created_at,
            "completed_at": project.completed_at
        }
    }

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a specific project and its data."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        # If the project was uploaded, it might be in the uploads directory
        # Let's clean up the folder to save space
        if "uploads" in project.source_path and os.path.exists(project.source_path):
            shutil.rmtree(project.source_path)
    except Exception as e:
        print(f"Failed to delete directory {project.source_path}: {e}")
            
    db.delete(project)
    db.commit()
    
    return {
        "status": "success",
        "data": None
    }

