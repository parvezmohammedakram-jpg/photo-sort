import cv2
import numpy as np
import os

from app.utils.logger import logger

# Initialize OpenCV Haar Cascades
# Use local cascade files instead of cv2.data which may be missing in some wheels
cascades_dir = os.path.join(os.path.dirname(__file__), 'cascades')
face_cascade_path = os.path.join(cascades_dir, 'haarcascade_frontalface_default.xml')
eye_cascade_path = os.path.join(cascades_dir, 'haarcascade_eye.xml')

face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

def analyze_faces(image: np.ndarray) -> dict:
    """
    Detect faces and analyze eye state using OpenCV Haar Cascades.
    This is a simpler, more robust fallback compared to MediaPipe which can have DLL issues.
    
    Args:
        image: BGR image array.
        
    Returns:
        dict: {
            "face_count": int,
            "closed_eye_detected": bool,
            "face_status": str
        }
    """
    try:
        # Convert BGR to Grayscale for Haar cascades
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        face_count = len(faces)
        if face_count == 0:
            return {
                "face_count": 0,
                "closed_eye_detected": False,
                "face_status": "no_face"
            }
            
        closed_eye_detected = False
        
        # For each face, try to detect eyes
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            
            # Detect eyes within the face ROI
            eyes = eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=10,
                minSize=(15, 15)
            )
            
            # Simple heuristic: if face is detected but < 2 eyes are detected, 
            # we might have a closed eye. (This is less accurate than EAR, but works as a fallback)
            # A better heuristic for Haar: often closed eyes aren't detected at all as 'eyes' by the standard cascade.
            if len(eyes) < 2:
                closed_eye_detected = True
                break
                
        status = "closed_eyes_detected" if closed_eye_detected else "faces_detected"
        
        return {
            "face_count": face_count,
            "closed_eye_detected": closed_eye_detected,
            "face_status": status
        }
        
    except Exception as e:
        logger.error(f"Face analysis failed: {e}")
        return {
            "face_count": 0,
            "closed_eye_detected": False,
            "face_status": "analysis_failed"
        }
