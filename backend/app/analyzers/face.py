import cv2
import numpy as np
import mediapipe as mp

from app.config import FACE_DETECTION_CONFIDENCE, EYE_CLOSED_THRESHOLD
from app.utils.logger import logger

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=10,
    refine_landmarks=True,
    min_detection_confidence=FACE_DETECTION_CONFIDENCE
)

# MediaPipe eye landmark indices
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def calculate_ear(eye_landmarks, all_landmarks, img_w, img_h) -> float:
    """
    Calculate Eye Aspect Ratio (EAR) given specific eye landmarks.
    Formula: EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    """
    def get_pt(idx):
        landmark = all_landmarks[idx]
        return np.array([landmark.x * img_w, landmark.y * img_h])
        
    p1 = get_pt(eye_landmarks[0]) # Outer corner
    p2 = get_pt(eye_landmarks[1]) # Top outer
    p3 = get_pt(eye_landmarks[2]) # Top inner
    p4 = get_pt(eye_landmarks[3]) # Inner corner
    p5 = get_pt(eye_landmarks[4]) # Bottom inner
    p6 = get_pt(eye_landmarks[5]) # Bottom outer
    
    # Compute Euclidean distances
    v1 = np.linalg.norm(p2 - p6)
    v2 = np.linalg.norm(p3 - p5)
    h = np.linalg.norm(p1 - p4)
    
    # Avoid division by zero (shouldn't happen with valid faces but safe)
    if h == 0:
        return 0.0
        
    ear = (v1 + v2) / (2.0 * h)
    return ear

def analyze_faces(image: np.ndarray) -> dict:
    """
    Detect faces and analyze eye state using MediaPipe Face Mesh.
    
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
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        
        # Process image
        results = face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return {
                "face_count": 0,
                "closed_eye_detected": False,
                "face_status": "no_face"
            }
            
        face_count = len(results.multi_face_landmarks)
        closed_eye_detected = False
        
        for face_landmarks in results.multi_face_landmarks:
            # Calculate EAR for both eyes
            left_ear = calculate_ear(LEFT_EYE, face_landmarks.landmark, w, h)
            right_ear = calculate_ear(RIGHT_EYE, face_landmarks.landmark, w, h)
            
            # Average EAR
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Check if eyes are closed
            if avg_ear < EYE_CLOSED_THRESHOLD:
                closed_eye_detected = True
                break # One closed-eye face is enough to flag the image
                
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
