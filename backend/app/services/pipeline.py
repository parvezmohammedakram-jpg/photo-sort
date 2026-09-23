"""
Main image analysis pipeline orchestrator.
"""

from sqlalchemy.orm import Session
import os

from app.models.photo import Photo
from app.models.project import Project
from app.models.analysis import Analysis, DuplicateGroup
from app.analyzers.blur import analyze_blur
from app.analyzers.exposure import analyze_exposure
from app.analyzers.face import analyze_faces
from app.analyzers.duplicate import calculate_hashes, compute_similarity
from app.analyzers.scorer import calculate_quality_score, determine_category
from app.utils.image_loader import load_image, resize_for_analysis, generate_thumbnail, generate_preview
from app.config import THUMBNAIL_DIR, PREVIEW_DIR
from app.utils.logger import logger

def process_single_photo(db: Session, photo: Photo) -> bool:
    """
    Run the full analysis pipeline on a single photo.
    
    Args:
        db: Database session
        photo: Photo ORM instance to process
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        logger.info(f"Processing photo {photo.id}: {photo.filename}")
        
        # 1. Generate thumbnail and preview (if they don't exist)
        thumb_path = str(THUMBNAIL_DIR / f"{photo.id}_{photo.filename}.jpg")
        preview_path = str(PREVIEW_DIR / f"{photo.id}_{photo.filename}.jpg")
        
        # Only generate if not already set (re-processing safety)
        if not photo.thumbnail_path:
            generated_thumb = generate_thumbnail(photo.filepath, thumb_path)
            if generated_thumb:
                photo.thumbnail_path = generated_thumb
                
            generate_preview(photo.filepath, preview_path)
            
        # 2. Load and resize image for memory-safe analysis
        image = load_image(photo.filepath)
        if image is None:
            raise ValueError(f"Could not load image: {photo.filepath}")
            
        analysis_image = resize_for_analysis(image)
        
        # 3. Run individual analyzers
        blur_results = analyze_blur(analysis_image)
        exposure_results = analyze_exposure(analysis_image)
        face_results = analyze_faces(image) # Use original high-res for better small face detection if possible, but MediaPipe resizes internally anyway
        hash_results = calculate_hashes(photo.filepath)
        
        # 4. Check for duplicates against already processed photos in this project
        # This is a basic O(n^2) approach suitable for moderate sized collections
        # It finds the first matching group or creates a new one
        duplicate_group_id = None
        is_duplicate = False
        
        if hash_results["perceptual_hash"]:
            # Find existing analyses in the same project with perceptual hashes
            existing_analyses = db.query(Analysis).join(Photo).filter(
                Photo.project_id == photo.project_id,
                Photo.id != photo.id,
                Analysis.duplicate_hash.isnot(None)
            ).all()
            
            for existing in existing_analyses:
                # 1. Check exact match
                if hash_results["exact_hash"] and existing.file_hash == hash_results["exact_hash"]:
                    is_duplicate = True
                    group_type = "exact"
                    
                    if existing.duplicate_group_id:
                        duplicate_group_id = existing.duplicate_group_id
                    else:
                        # Create new group
                        group = DuplicateGroup(
                            project_id=photo.project_id,
                            group_type=group_type,
                            similarity_score=0.0,
                            member_count=2 # Will be updated
                        )
                        db.add(group)
                        db.flush()
                        existing.duplicate_group_id = group.id
                        duplicate_group_id = group.id
                    break
                    
                # 2. Check near-duplicate (perceptual)
                from app.config import DUPLICATE_HASH_THRESHOLD
                distance = compute_similarity(hash_results["perceptual_hash"], existing.duplicate_hash)
                
                if distance <= DUPLICATE_HASH_THRESHOLD:
                    is_duplicate = True
                    group_type = "near_duplicate"
                    
                    if existing.duplicate_group_id:
                        duplicate_group_id = existing.duplicate_group_id
                    else:
                        # Create new group
                        group = DuplicateGroup(
                            project_id=photo.project_id,
                            group_type=group_type,
                            similarity_score=float(distance),
                            member_count=2
                        )
                        db.add(group)
                        db.flush()
                        existing.duplicate_group_id = group.id
                        duplicate_group_id = group.id
                    break
                    
        # 5. Calculate final quality score
        score = calculate_quality_score(
            sharpness_var=blur_results["sharpness_score"],
            brightness_avg=exposure_results["brightness_avg"],
            face_status=face_results["face_status"],
            megapixels=photo.megapixels,
            is_duplicate=is_duplicate
        )
        
        category = determine_category(score)
        
        # 6. Save Analysis record
        # If re-processing, get existing analysis
        analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
        if not analysis:
            analysis = Analysis(photo_id=photo.id)
            db.add(analysis)
            
        # Populate fields
        analysis.sharpness_score = blur_results["sharpness_score"]
        analysis.blur_status = blur_results["blur_status"]
        
        analysis.brightness_avg = exposure_results["brightness_avg"]
        analysis.dark_pixel_pct = exposure_results["dark_pixel_pct"]
        analysis.bright_pixel_pct = exposure_results["bright_pixel_pct"]
        analysis.exposure_status = exposure_results["exposure_status"]
        
        analysis.face_count = face_results["face_count"]
        analysis.closed_eye_detected = face_results["closed_eye_detected"]
        analysis.face_status = face_results["face_status"]
        
        analysis.duplicate_hash = hash_results["perceptual_hash"]
        analysis.file_hash = hash_results["exact_hash"]
        analysis.duplicate_group_id = duplicate_group_id
        
        analysis.quality_score = score
        analysis.category = category
        
        photo.status = "processed"
        db.commit()
        
        # Update group counts if added to a group
        if duplicate_group_id:
            group = db.query(DuplicateGroup).get(duplicate_group_id)
            group.member_count = db.query(Analysis).filter(Analysis.duplicate_group_id == group.id).count()
            db.commit()
            
        return True
        
    except Exception as e:
        logger.error(f"Error processing photo {photo.id}: {e}")
        photo.status = "failed"
        photo.error_message = str(e)
        db.commit()
        return False

def run_analysis_pipeline(project_id: int):
    """
    Background task to process all pending photos in a project.
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        project = db.query(Project).get(project_id)
        if not project:
            logger.error(f"Project {project_id} not found for processing")
            return
            
        project.status = "processing"
        db.commit()
        
        photos = db.query(Photo).filter(
            Photo.project_id == project_id,
            Photo.status == "pending"
        ).all()
        
        for photo in photos:
            success = process_single_photo(db, photo)
            if success:
                project.processed_files += 1
            else:
                project.failed_files += 1
                
            db.commit() # Commit project progress incrementally
            
        # Update project status
        project.status = "completed"
        from datetime import datetime
        project.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Project {project_id} processing completed.")
        
    except Exception as e:
        logger.error(f"Pipeline failed for project {project_id}: {e}")
        if project:
            project.status = "failed"
            db.commit()
    finally:
        db.close()
