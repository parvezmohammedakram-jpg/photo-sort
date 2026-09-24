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

import concurrent.futures

def analyze_image_worker(photo_id: int, filepath: str, filename: str, has_thumbnail: bool):
    """
    Pure CPU worker for image analysis. No database interactions.
    """
    import cv2
    cv2.setNumThreads(1)
    try:
        # 1. Generate thumbnail and preview (if they don't exist)
        thumb_path = str(THUMBNAIL_DIR / f"{photo_id}_{filename}.jpg")
        preview_path = str(PREVIEW_DIR / f"{photo_id}_{filename}.jpg")
        
        generated_thumb = None
        if not has_thumbnail:
            generated_thumb = generate_thumbnail(filepath, thumb_path)
            generate_preview(filepath, preview_path)
            
        # 2. Load and resize image for memory-safe analysis
        image = load_image(filepath)
        if image is None:
            return {"photo_id": photo_id, "success": False, "error": f"Could not load image: {filepath}"}
            
        analysis_image = resize_for_analysis(image)
        
        # 3. Run individual analyzers
        blur_results = analyze_blur(analysis_image)
        exposure_results = analyze_exposure(analysis_image)
        face_results = analyze_faces(analysis_image)
        hash_results = calculate_hashes(filepath)
        
        return {
            "photo_id": photo_id,
            "success": True,
            "generated_thumb": generated_thumb,
            "blur_results": blur_results,
            "exposure_results": exposure_results,
            "face_results": face_results,
            "hash_results": hash_results,
        }
    except Exception as e:
        return {"photo_id": photo_id, "success": False, "error": str(e)}

def process_single_photo_db(db: Session, photo: Photo, result: dict, duplicate_cache: list) -> bool:
    """
    Process the dictionary returned by analyze_image_worker and save it to the database.
    """
    try:
        if not result["success"]:
            logger.error(f"Error processing photo {photo.id}: {result.get('error')}")
            photo.status = "failed"
            photo.error_message = result.get("error")
            return False
            
        if result["generated_thumb"] and not photo.thumbnail_path:
            photo.thumbnail_path = result["generated_thumb"]
            
        blur_results = result["blur_results"]
        exposure_results = result["exposure_results"]
        face_results = result["face_results"]
        hash_results = result["hash_results"]
        
        duplicate_group_id = None
        is_duplicate = False
        
        if hash_results["perceptual_hash"]:
            for existing in duplicate_cache:
                if existing["photo_id"] == photo.id:
                    continue
                    
                if hash_results["exact_hash"] and existing["file_hash"] == hash_results["exact_hash"]:
                    is_duplicate = True
                    group_type = "exact"
                    
                    if existing["duplicate_group_id"]:
                        duplicate_group_id = existing["duplicate_group_id"]
                    else:
                        group = DuplicateGroup(
                            project_id=photo.project_id,
                            group_type=group_type,
                            similarity_score=0.0,
                            member_count=2
                        )
                        db.add(group)
                        db.flush()
                        db.query(Analysis).filter(Analysis.id == existing["id"]).update({"duplicate_group_id": group.id})
                        existing["duplicate_group_id"] = group.id
                        duplicate_group_id = group.id
                    break
                    
                from app.config import DUPLICATE_HASH_THRESHOLD
                distance = compute_similarity(hash_results["perceptual_hash"], existing.get("parsed_hash") or existing["duplicate_hash"])
                
                if distance <= DUPLICATE_HASH_THRESHOLD:
                    is_duplicate = True
                    group_type = "near_duplicate"
                    
                    if existing["duplicate_group_id"]:
                        duplicate_group_id = existing["duplicate_group_id"]
                    else:
                        group = DuplicateGroup(
                            project_id=photo.project_id,
                            group_type=group_type,
                            similarity_score=float(distance),
                            member_count=2
                        )
                        db.add(group)
                        db.flush()
                        db.query(Analysis).filter(Analysis.id == existing["id"]).update({"duplicate_group_id": group.id})
                        existing["duplicate_group_id"] = group.id
                        duplicate_group_id = group.id
                    break
                    
        score = calculate_quality_score(
            sharpness_var=blur_results["sharpness_score"],
            brightness_avg=exposure_results["brightness_avg"],
            face_status=face_results["face_status"],
            megapixels=photo.megapixels,
            is_duplicate=is_duplicate
        )
        
        category = determine_category(score)
        
        analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
        if not analysis:
            analysis = Analysis(photo_id=photo.id)
            db.add(analysis)
            
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
        db.flush()
        
        import imagehash
        duplicate_cache.append({
            "id": analysis.id,
            "file_hash": analysis.file_hash,
            "duplicate_hash": analysis.duplicate_hash,
            "parsed_hash": imagehash.hex_to_hash(hash_results["perceptual_hash"]) if hash_results["perceptual_hash"] else None,
            "duplicate_group_id": analysis.duplicate_group_id,
            "photo_id": photo.id
        })
        
        if duplicate_group_id:
            group = db.query(DuplicateGroup).get(duplicate_group_id)
            group.member_count = db.query(Analysis).filter(Analysis.duplicate_group_id == group.id).count()
            
        return True
        
    except Exception as e:
        logger.error(f"Error saving DB for photo {photo.id}: {e}")
        photo.status = "failed"
        photo.error_message = str(e)
        return False

def run_analysis_pipeline(project_id: int):
    """
    Background task to process all pending photos in a project using multiple CPU cores.
    """
    from app.database import SessionLocal
    from datetime import datetime
    
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
        
        worker_args = [
            (photo.id, photo.filepath, photo.filename, bool(photo.thumbnail_path))
            for photo in photos
        ]
        
        # Load cache once
        existing_analyses = db.query(Analysis).join(Photo).filter(
            Photo.project_id == project_id,
            Analysis.duplicate_hash.isnot(None)
        ).all()
        import imagehash
        duplicate_cache = [
            {
                "id": a.id,
                "file_hash": a.file_hash,
                "duplicate_hash": a.duplicate_hash,
                "parsed_hash": imagehash.hex_to_hash(a.duplicate_hash) if a.duplicate_hash else None,
                "duplicate_group_id": a.duplicate_group_id,
                "photo_id": a.photo_id
            }
            for a in existing_analyses
        ]
        
        logger.info(f"Starting sequential processing for {len(worker_args)} photos.")
        
        processed_count = 0
        for args in worker_args:
            result = analyze_image_worker(*args)
            
            # Fetch fresh photo object
            photo = db.query(Photo).get(result["photo_id"])
            if photo:
                success = process_single_photo_db(db, photo, result, duplicate_cache)
                if success:
                    project.processed_files += 1
                else:
                    project.failed_files += 1
                    
                processed_count += 1
                # Commit project progress more frequently so UI updates in real-time
                if processed_count % 2 == 0:
                    db.commit()
            
        # Update project status
        project.status = "completed"
        project.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Project {project_id} processing completed.")
        
    except Exception as e:
        logger.error(f"Pipeline failed for project {project_id}: {e}")
        if 'project' in locals() and project:
            project.status = "failed"
            db.commit()
    finally:
        db.close()
