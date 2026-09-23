import pytest
import numpy as np
import cv2

from app.analyzers.blur import analyze_blur
from app.config import BLUR_SHARP_THRESHOLD, BLUR_BORDERLINE_THRESHOLD

def test_analyze_blur_sharp():
    """Test blur analysis on a simulated sharp image (high variance)."""
    # Create an image with high contrast edges (checkerboard pattern)
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[0:50, 0:50] = 255
    image[50:100, 50:100] = 255
    
    result = analyze_blur(image)
    
    assert result["sharpness_score"] >= BLUR_SHARP_THRESHOLD
    assert result["blur_status"] == "sharp"

def test_analyze_blur_blurry():
    """Test blur analysis on a simulated blurry image (low variance)."""
    # Create a uniform gray image (zero variance)
    image = np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    result = analyze_blur(image)
    
    assert result["sharpness_score"] < BLUR_BORDERLINE_THRESHOLD
    assert result["blur_status"] == "blurry"

def test_analyze_blur_invalid_input():
    """Test blur analysis with invalid input (should fail gracefully)."""
    # Pass None instead of a numpy array
    result = analyze_blur(None)
    
    assert result["sharpness_score"] == 0.0
    assert result["blur_status"] == "analysis_failed"
