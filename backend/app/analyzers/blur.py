import cv2
import numpy as np

from app.config import BLUR_SHARP_THRESHOLD, BLUR_BORDERLINE_THRESHOLD
from app.utils.logger import logger

def analyze_blur(image: np.ndarray) -> dict:
    """
    Detect blur using the variance of the Laplacian method.
    
    Args:
        image: BGR image array (preferably resized for performance).
        
    Returns:
        dict: {
            "sharpness_score": float,
            "blur_status": str ("sharp", "borderline", "blurry")
        }
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Categorize
        if variance >= BLUR_SHARP_THRESHOLD:
            status = "sharp"
        elif variance >= BLUR_BORDERLINE_THRESHOLD:
            status = "borderline"
        else:
            status = "blurry"
            
        return {
            "sharpness_score": float(variance),
            "blur_status": status
        }
        
    except Exception as e:
        logger.error(f"Blur analysis failed: {e}")
        return {
            "sharpness_score": 0.0,
            "blur_status": "analysis_failed"
        }
