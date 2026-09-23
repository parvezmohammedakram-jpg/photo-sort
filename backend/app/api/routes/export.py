import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.schemas.base import APIResponse
from app.schemas.export import ExportRequest, ExportStatus
from app.models.project import Project
from app.services.export import execute_export, get_export_status

router = APIRouter(prefix="/export", tags=["export"])

@router.post("", response_model=APIResponse[dict])
def start_export(request: ExportRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Initiate an export job in the background."""
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    task_id = str(uuid.uuid4())
    
    # We need a new session for the background task
    bg_db = SessionLocal()
    
    background_tasks.add_task(
        execute_export,
        task_id=task_id,
        db=bg_db,
        project_id=request.project_id,
        dest_path=request.destination_path,
        categories=request.categories
    )
    
    return {
        "status": "success",
        "data": {
            "task_id": task_id
        }
    }

@router.get("/{task_id}", response_model=APIResponse[ExportStatus])
def check_export_status(task_id: str):
    """Check the status of an ongoing export job."""
    status_data = get_export_status(task_id)
    
    if not status_data:
        raise HTTPException(status_code=404, detail="Export task not found")
        
    return {
        "status": "success",
        "data": status_data
    }
