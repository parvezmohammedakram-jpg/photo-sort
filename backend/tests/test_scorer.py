import pytest

from app.analyzers.scorer import (
    calculate_quality_score,
    determine_category,
    normalize_sharpness,
    normalize_exposure,
    normalize_face,
    normalize_resolution
)
from app.config import EXPOSURE_IDEAL_LOW, TARGET_MEGAPIXELS

def test_normalize_sharpness():
    assert normalize_sharpness(0) == 0.0
    assert normalize_sharpness(250) == 50.0
    assert normalize_sharpness(500) == 100.0
    assert normalize_sharpness(1000) == 100.0  # Capped

def test_normalize_exposure():
    # Ideal range gets 100
    assert normalize_exposure(EXPOSURE_IDEAL_LOW) == 100.0
    
    # Too dark
    assert normalize_exposure(0) == 0.0
    
    # Too bright
    assert normalize_exposure(255) == 0.0

def test_normalize_face():
    assert normalize_face("faces_detected") == 100.0
    assert normalize_face("no_face") == 100.0 # Landscapes not penalized
    assert normalize_face("closed_eyes_detected") == 0.0

def test_normalize_resolution():
    assert normalize_resolution(0) == 0.0
    assert normalize_resolution(TARGET_MEGAPIXELS / 2) == 50.0
    assert normalize_resolution(TARGET_MEGAPIXELS) == 100.0
    assert normalize_resolution(TARGET_MEGAPIXELS * 2) == 100.0 # Capped

def test_calculate_quality_score_perfect():
    score = calculate_quality_score(
        sharpness_var=500,        # 100 normalized
        brightness_avg=120,       # 100 normalized
        face_status="faces_detected", # 100 normalized
        megapixels=TARGET_MEGAPIXELS, # 100 normalized
        is_duplicate=False
    )
    assert score == 100.0

def test_determine_category():
    assert determine_category(80.0) == "good"
    assert determine_category(70.0) == "good"
    assert determine_category(69.9) == "review"
    assert determine_category(40.0) == "review"
    assert determine_category(39.9) == "poor"
    assert determine_category(0.0) == "poor"
