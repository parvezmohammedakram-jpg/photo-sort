import cv2
import numpy as np

from app.config import (
    EXPOSURE_LOW_BRIGHTNESS,
    EXPOSURE_HIGH_BRIGHTNESS,
    DARK_PIXEL_THRESHOLD,
    BRIGHT_PIXEL_THRESHOLD,
    DARK_PIXEL_PCT_THRESHOLD,
    BRIGHT_PIXEL_PCT_THRESHOLD
)
from app.utils.logger import logger

def analyze_exposure(image: np.ndarray) -> dict:
    """
    Analyze image exposure using average brightness and histogram distribution.
    
    Args:
        image: BGR image array.
        
    Returns:
        dict: {
            "brightness_avg": float,
            "dark_pixel_pct": float,
            "bright_pixel_pct": float,
            "exposure_status": str ("good", "underexposed", "overexposed")
        }
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Average Brightness
        brightness_avg = np.mean(gray)
        
        # 2. Pixel Distribution (Histogram based)
        total_pixels = gray.size
        
        dark_pixels = np.sum(gray < DARK_PIXEL_THRESHOLD)
        bright_pixels = np.sum(gray > BRIGHT_PIXEL_THRESHOLD)
        
        dark_pct = (dark_pixels / total_pixels) * 100
        bright_pct = (bright_pixels / total_pixels) * 100
        
        # 3. Categorization logic
        if brightness_avg < EXPOSURE_LOW_BRIGHTNESS or dark_pct > DARK_PIXEL_PCT_THRESHOLD:
            status = "underexposed"
        elif brightness_avg > EXPOSURE_HIGH_BRIGHTNESS or bright_pct > BRIGHT_PIXEL_PCT_THRESHOLD:
            status = "overexposed"
        else:
            status = "good"
            
        return {
            "brightness_avg": float(brightness_avg),
            "dark_pixel_pct": float(dark_pct),
            "bright_pixel_pct": float(bright_pct),
            "exposure_status": status
        }
        
    except Exception as e:
        logger.error(f"Exposure analysis failed: {e}")
        return {
            "brightness_avg": 0.0,
            "dark_pixel_pct": 0.0,
            "bright_pixel_pct": 0.0,
            "exposure_status": "analysis_failed"
        }
