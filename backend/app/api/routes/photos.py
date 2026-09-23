from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.schemas.base import APIResponse
from app.schemas.photo import PhotoListResponse, PhotoDetailResponse, StatisticsResponse, PhotoCategoryUpdate, PhotoCategoryUpdateResponse
from app.models.photo import Photo
from app.models.project import Project
from app.models.analysis import Analysis, DuplicateGroup
from app.models.review import ManualReview

router = APIRouter(prefix="/photos", tags=["photos"])

@router.get("", response_model=APIResponse[List[PhotoListResponse]])
def list_photos(
    project_id: int,
    category: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db)
):
    """List photos for a project with optional category filtering."""
    query = db.query(Photo).filter(Photo.project_id == project_id)
    
    if category:
        query = query.join(Analysis).filter(Analysis.category == category)
        
    total = query.count()
    
    photos = query.order_by(Photo.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    # We need to map ORM objects to the response schema, extracting nested analysis data
    response_data = []
    for photo in photos:
        analysis = photo.analysis
        response_data.append({
            "id": photo.id,
            "filename": photo.filename,
            "thumbnail_url": f"/api/files/thumbnails/{photo.id}_{photo.filename}.jpg" if photo.thumbnail_path else None,
            "quality_score": analysis.quality_score if analysis else None,
            "category": analysis.category if analysis else "pending",
            "blur_status": analysis.blur_status if analysis else None,
            "exposure_status": analysis.exposure_status if analysis else None,
            "face_count": analysis.face_count if analysis else 0,
            "is_duplicate": analysis.duplicate_group_id is not None if analysis else False,
            "is_manually_modified": analysis.is_manually_modified if analysis else False
        })
        
    total_pages = (total + per_page - 1) // per_page
        
    return {
        "status": "success",
        "data": response_data,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    }

@router.get("/{photo_id}", response_model=APIResponse[PhotoDetailResponse])
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a single photo."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
        
    # Compile detected issues based on thresholds
    detected_issues = []
    if photo.analysis:
        analysis = photo.analysis
        if analysis.blur_status in ("borderline", "blurry"):
            detected_issues.append("Image lacks sharpness")
        if analysis.exposure_status == "underexposed":
            detected_issues.append("Image is underexposed (too dark)")
        elif analysis.exposure_status == "overexposed":
            detected_issues.append("Image is overexposed (too bright)")
        if analysis.closed_eye_detected:
            detected_issues.append("Closed eyes detected")
        if analysis.duplicate_group_id:
            detected_issues.append("Duplicate or near-duplicate detected")
            
    response_data = {
        "id": photo.id,
        "filename": photo.filename,
        "filepath": photo.filepath,
        "file_size": photo.file_size,
        "width": photo.width,
        "height": photo.height,
        "megapixels": photo.megapixels,
        "format": photo.format,
        "thumbnail_url": f"/api/files/thumbnails/{photo.id}_{photo.filename}.jpg" if photo.thumbnail_path else None,
        "preview_url": f"/api/files/previews/{photo.id}_{photo.filename}.jpg" if photo.thumbnail_path else None,
        "status": photo.status,
        "analysis": photo.analysis,
        "detected_issues": detected_issues,
        "created_at": photo.created_at
    }
        
    return {
        "status": "success",
        "data": response_data
    }

@router.get("/project/{project_id}/stats", response_model=APIResponse[StatisticsResponse])
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    """Get aggregate statistics for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Get category counts
    categories = {"good": 0, "review": 0, "poor": 0, "pending": 0}
    category_counts = db.query(Analysis.category, func.count(Analysis.id))\
        .join(Photo).filter(Photo.project_id == project_id)\
        .group_by(Analysis.category).all()
        
    for cat, count in category_counts:
        categories[cat] = count
        
    # Duplicate stats
    duplicate_groups = db.query(DuplicateGroup).filter(DuplicateGroup.project_id == project_id).count()
    duplicate_photos = db.query(Analysis).join(Photo).filter(
        Photo.project_id == project_id, 
        Analysis.duplicate_group_id.isnot(None)
    ).count()
    
    # Average score
    avg_score = db.query(func.avg(Analysis.quality_score))\
        .join(Photo).filter(Photo.project_id == project_id).scalar() or 0.0
        
    # Issue counts
    issues = {
        "blur": db.query(Analysis).join(Photo).filter(Photo.project_id == project_id, Analysis.blur_status != "sharp").count(),
        "exposure": db.query(Analysis).join(Photo).filter(Photo.project_id == project_id, Analysis.exposure_status != "good").count(),
        "eyes_closed": db.query(Analysis).join(Photo).filter(Photo.project_id == project_id, Analysis.closed_eye_detected == True).count()
    }
    
    return {
        "status": "success",
        "data": {
            "total_photos": project.total_files,
            "processed": project.processed_files,
            "failed": project.failed_files,
            "categories": categories,
            "duplicate_groups": duplicate_groups,
            "duplicate_photos": duplicate_photos,
            "average_quality_score": round(avg_score, 1),
            "issues": issues
        }
    }

@router.patch("/{photo_id}/category", response_model=APIResponse[PhotoCategoryUpdateResponse])
def update_photo_category(photo_id: int, update: PhotoCategoryUpdate, db: Session = Depends(get_db)):
    """Manually override a photo's category."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo or not photo.analysis:
        raise HTTPException(status_code=404, detail="Photo or analysis not found")
        
    analysis = photo.analysis
    
    if update.category not in ["good", "review", "poor"]:
        raise HTTPException(status_code=400, detail="Invalid category")
        
    old_category = analysis.category
    
    if old_category != update.category:
        # Update category and flag
        analysis.category = update.category
        analysis.is_manually_modified = True
        
        # Log review
        review = ManualReview(
            photo_id=photo_id,
            previous_category=old_category,
            new_category=update.category,
            reason="Manual override via UI"
        )
        db.add(review)
        db.commit()
        
    return {
        "status": "success",
        "data": {
            "id": photo.id,
            "category": analysis.category,
            "is_manually_modified": analysis.is_manually_modified
        }
    }
