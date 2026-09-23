"""
Ingestion service.
Handles project creation, file discovery, and database population.
"""

from pathlib import Path
from sqlalchemy.orm import Session
import os

from app.models.project import Project
from app.models.photo import Photo
from app.utils.file_utils import discover_images, validate_directory_path
from app.utils.image_loader import validate_image, get_image_dimensions
from app.utils.logger import logger

def create_project(db: Session, name: str, source_path: str) -> Project:
    """
    Create a new project and discover images in the source path.
    """
    source_path = source_path.strip().strip('"').strip("'")
    
    # 1. Validate directory
    is_valid, err_msg = validate_directory_path(source_path)
    if not is_valid:
        raise ValueError(err_msg)
        
    # 2. Create project record
    project = Project(
        name=name,
        source_path=str(Path(source_path).resolve())
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # 3. Discover files
    supported_files, skipped_files = discover_images(source_path)
    
    total_found = len(supported_files) + len(skipped_files)
    project.total_files = total_found
    project.supported_files = len(supported_files)
    
    # 4. Create photo records for supported files
    photos_to_create = []
    
    for file_path in supported_files:
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Create pending photo record
            photo = Photo(
                project_id=project.id,
                filename=file_path.name,
                filepath=str(file_path),
                file_size=file_size,
                format=file_path.suffix.lower().lstrip('.'),
                status="pending"
            )
            
            # Optional: Read dimensions now (fast using PIL)
            dimensions = get_image_dimensions(str(file_path))
            if dimensions:
                w, h = dimensions
                photo.width = w
                photo.height = h
                photo.megapixels = (w * h) / 1_000_000
                
            photos_to_create.append(photo)
            
        except Exception as e:
            logger.error(f"Error accessing file {file_path}: {e}")
            
    if photos_to_create:
        db.add_all(photos_to_create)
        
    db.commit()
    db.refresh(project)
    
    logger.info(f"Created project {project.id}: found {len(supported_files)} supported images.")
    return project
