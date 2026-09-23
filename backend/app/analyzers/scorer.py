"""
Quality scoring engine implementation.
Matches the algorithm defined in 10-scoring-engine.md.
"""

from app.config import (
    WEIGHT_SHARPNESS,
    WEIGHT_EXPOSURE,
    WEIGHT_FACE,
    WEIGHT_RESOLUTION,
    EXPOSURE_IDEAL_LOW,
    EXPOSURE_IDEAL_HIGH,
    TARGET_MEGAPIXELS,
    GOOD_THRESHOLD,
    REVIEW_THRESHOLD,
    DUPLICATE_PENALTY
)
from app.utils.logger import logger

def normalize_sharpness(variance: float) -> float:
    """Normalize Laplacian variance (0-500+) to 0-100 scale."""
    if variance is None:
        return 0.0
    # Capping at 500 as "perfectly sharp" for normalization purposes
    capped = min(max(variance, 0), 500)
    return (capped / 500) * 100

def normalize_exposure(brightness: float) -> float:
    """
    Normalize brightness (0-255).
    Peak score (100) at ideal range (80-180).
    Penalty drops linearly towards 0 and 255.
    """
    if brightness is None:
        return 0.0
        
    if EXPOSURE_IDEAL_LOW <= brightness <= EXPOSURE_IDEAL_HIGH:
        return 100.0
        
    if brightness < EXPOSURE_IDEAL_LOW:
        # Distance from ideal low
        dist = EXPOSURE_IDEAL_LOW - brightness
        score = 100 - ((dist / EXPOSURE_IDEAL_LOW) * 100)
    else:
        # Distance from ideal high
        dist = brightness - EXPOSURE_IDEAL_HIGH
        range_high = 255 - EXPOSURE_IDEAL_HIGH
        score = 100 - ((dist / range_high) * 100)
        
    return max(0.0, score)

def normalize_face(face_status: str) -> float:
    """
    Score based on face presence and eye state.
    100 = Faces detected (eyes open) OR No faces (doesn't penalize landscapes)
    0 = Closed eyes detected
    """
    if face_status == "closed_eyes_detected":
        return 0.0
    # Both "faces_detected" and "no_face" get 100
    # This prevents landscapes from being penalized
    return 100.0

def normalize_resolution(megapixels: float) -> float:
    """
    Normalize resolution based on a target (e.g. 8MP).
    """
    if megapixels is None or megapixels <= 0:
        return 0.0
        
    capped = min(megapixels, TARGET_MEGAPIXELS)
    return (capped / TARGET_MEGAPIXELS) * 100

def calculate_quality_score(
    sharpness_var: float,
    brightness_avg: float,
    face_status: str,
    megapixels: float,
    is_duplicate: bool = False
) -> float:
    """
    Calculate the final weighted quality score.
    """
    try:
        norm_sharp = normalize_sharpness(sharpness_var)
        norm_exp = normalize_exposure(brightness_avg)
        norm_face = normalize_face(face_status)
        norm_res = normalize_resolution(megapixels)
        
        base_score = (
            (norm_sharp * WEIGHT_SHARPNESS) +
            (norm_exp * WEIGHT_EXPOSURE) +
            (norm_face * WEIGHT_FACE) +
            (norm_res * WEIGHT_RESOLUTION)
        )
        
        # Apply duplicate penalty
        if is_duplicate:
            base_score -= DUPLICATE_PENALTY
            
        # Ensure score stays in 0-100 range
        return max(0.0, min(100.0, base_score))
        
    except Exception as e:
        logger.error(f"Scoring calculation failed: {e}")
        return 0.0

def determine_category(score: float) -> str:
    """Determine category based on final score."""
    if score >= GOOD_THRESHOLD:
        return "good"
    elif score >= REVIEW_THRESHOLD:
        return "review"
    else:
        return "poor"
