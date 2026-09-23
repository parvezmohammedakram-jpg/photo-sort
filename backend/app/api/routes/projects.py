from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectProcessingStatus
from app.schemas.base import APIResponse
from app.models.project import Project
from app.services.ingestion import create_project

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
        
        # Here we would normally trigger the background analysis pipeline
        # background_tasks.add_task(run_analysis_pipeline, project.id)
        
        return {
            "status": "success",
            "data": project
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

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
            "progress_percent": round(percent, 1)
        }
    }
