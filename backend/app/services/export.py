import shutil
from pathlib import Path
import os
import uuid
from typing import List

from sqlalchemy.orm import Session
from app.models.photo import Photo
from app.models.analysis import Analysis
from app.utils.logger import logger

# Store export progress in-memory for simplicity.
# In a production app, you might use Redis or a DB table for this.
_export_tasks = {}

def get_export_status(task_id: str) -> dict:
    return _export_tasks.get(task_id)

def execute_export(task_id: str, db: Session, project_id: int, dest_path: str, categories: List[str]):
    """Background task to safely copy files."""
    _export_tasks[task_id] = {
        "status": "processing",
        "total_files": 0,
        "copied_files": 0,
        "failed_files": 0,
        "error_message": None
    }
    
    try:
        dest_dir = Path(dest_path)
        
        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Query photos matching categories
        photos = db.query(Photo).join(Analysis).filter(
            Photo.project_id == project_id,
            Analysis.category.in_(categories)
        ).all()
        
        _export_tasks[task_id]["total_files"] = len(photos)
        
        if len(photos) == 0:
            _export_tasks[task_id]["status"] = "completed"
            return
            
        for photo in photos:
            try:
                src_path = Path(photo.filepath)
                if not src_path.exists():
                    raise FileNotFoundError(f"Source file not found: {src_path}")
                    
                # Handle filename collisions in destination
                filename = src_path.name
                target_path = dest_dir / filename
                counter = 1
                while target_path.exists():
                    target_path = dest_dir / f"{src_path.stem}_{counter}{src_path.suffix}"
                    counter += 1
                    
                # Safely copy file (preserves metadata where possible, does not delete original)
                shutil.copy2(src_path, target_path)
                
                _export_tasks[task_id]["copied_files"] += 1
                
            except Exception as e:
                logger.error(f"Failed to export photo {photo.id}: {e}")
                _export_tasks[task_id]["failed_files"] += 1
                
        _export_tasks[task_id]["status"] = "completed"
        
    except Exception as e:
        logger.error(f"Export task {task_id} failed: {e}")
        _export_tasks[task_id]["status"] = "failed"
        _export_tasks[task_id]["error_message"] = str(e)
    finally:
        db.close()
