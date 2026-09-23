from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.schemas.base import APIResponse
from app.models.photo import Photo
from app.models.project import Project
from app.models.analysis import Analysis, DuplicateGroup

router = APIRouter(prefix="/duplicates", tags=["duplicates"])

@router.get("/project/{project_id}")
def get_duplicate_groups(project_id: int, db: Session = Depends(get_db)):
    """Get all duplicate groups for a project, including their photos."""
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Get all groups
    groups = db.query(DuplicateGroup).filter(
        DuplicateGroup.project_id == project_id,
        DuplicateGroup.member_count > 1
    ).order_by(DuplicateGroup.member_count.desc()).all()
    
    response_data = []
    
    for group in groups:
        # Get photos for this group
        photos = db.query(Photo).join(Analysis).filter(
            Analysis.duplicate_group_id == group.id
        ).all()
        
        group_photos = []
        for photo in photos:
            analysis = photo.analysis
            group_photos.append({
                "id": photo.id,
                "filename": photo.filename,
                "thumbnail_url": f"/api/files/thumbnails/{photo.id}_{photo.filename}.jpg" if photo.thumbnail_path else None,
                "quality_score": analysis.quality_score if analysis else None,
                "category": analysis.category if analysis else "pending",
                "megapixels": photo.megapixels,
                "file_size": photo.file_size
            })
            
        # Sort photos within group by quality score (highest first)
        group_photos.sort(key=lambda x: (x["quality_score"] or 0), reverse=True)
        
        response_data.append({
            "group_id": group.id,
            "group_type": group.group_type,
            "similarity_score": group.similarity_score,
            "member_count": group.member_count,
            "photos": group_photos
        })
        
    return {
        "status": "success",
        "data": response_data
    }
