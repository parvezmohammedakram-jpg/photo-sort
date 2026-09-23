"""
Centralized configuration for PhotoSort.

All thresholds, weights, and settings are defined here.
Values are loaded from environment variables with sensible defaults.
No threshold should be hard-coded in individual modules.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
PREVIEW_DIR = DATA_DIR / "previews"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
THUMBNAIL_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'photosort.db'}")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))


# ---------------------------------------------------------------------------
# Supported File Extensions
# ---------------------------------------------------------------------------
_ext_str = os.getenv("SUPPORTED_EXTENSIONS", ".jpg,.jpeg,.png,.webp")
SUPPORTED_EXTENSIONS = set(ext.strip().lower() for ext in _ext_str.split(","))


# ---------------------------------------------------------------------------
# Blur Detection Thresholds
# ---------------------------------------------------------------------------
BLUR_SHARP_THRESHOLD = float(os.getenv("BLUR_SHARP_THRESHOLD", "100.0"))
BLUR_BORDERLINE_THRESHOLD = float(os.getenv("BLUR_BORDERLINE_THRESHOLD", "50.0"))


# ---------------------------------------------------------------------------
# Resolution Thresholds
# ---------------------------------------------------------------------------
MIN_WIDTH = int(os.getenv("MIN_WIDTH", "1280"))
MIN_HEIGHT = int(os.getenv("MIN_HEIGHT", "720"))
MIN_MEGAPIXELS = float(os.getenv("MIN_MEGAPIXELS", "1.0"))
TARGET_MEGAPIXELS = float(os.getenv("TARGET_MEGAPIXELS", "8.0"))


# ---------------------------------------------------------------------------
# Exposure Thresholds
# ---------------------------------------------------------------------------
EXPOSURE_LOW_BRIGHTNESS = float(os.getenv("EXPOSURE_LOW_BRIGHTNESS", "60"))
EXPOSURE_HIGH_BRIGHTNESS = float(os.getenv("EXPOSURE_HIGH_BRIGHTNESS", "200"))
DARK_PIXEL_THRESHOLD = int(os.getenv("DARK_PIXEL_THRESHOLD", "30"))
BRIGHT_PIXEL_THRESHOLD = int(os.getenv("BRIGHT_PIXEL_THRESHOLD", "225"))
DARK_PIXEL_PCT_THRESHOLD = float(os.getenv("DARK_PIXEL_PCT_THRESHOLD", "40.0"))
BRIGHT_PIXEL_PCT_THRESHOLD = float(os.getenv("BRIGHT_PIXEL_PCT_THRESHOLD", "40.0"))


# ---------------------------------------------------------------------------
# Exposure Ideal Range (for scoring normalization)
# ---------------------------------------------------------------------------
EXPOSURE_IDEAL_LOW = float(os.getenv("EXPOSURE_IDEAL_LOW", "80"))
EXPOSURE_IDEAL_HIGH = float(os.getenv("EXPOSURE_IDEAL_HIGH", "180"))


# ---------------------------------------------------------------------------
# Face Detection Thresholds
# ---------------------------------------------------------------------------
FACE_DETECTION_CONFIDENCE = float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.5"))
EYE_CLOSED_THRESHOLD = float(os.getenv("EYE_CLOSED_THRESHOLD", "0.18"))


# ---------------------------------------------------------------------------
# Duplicate Detection Thresholds
# ---------------------------------------------------------------------------
DUPLICATE_HASH_THRESHOLD = int(os.getenv("DUPLICATE_HASH_THRESHOLD", "10"))
DUPLICATE_HASH_SIZE = int(os.getenv("DUPLICATE_HASH_SIZE", "16"))


# ---------------------------------------------------------------------------
# Scoring Weights (must sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHT_SHARPNESS = float(os.getenv("WEIGHT_SHARPNESS", "0.35"))
WEIGHT_RESOLUTION = float(os.getenv("WEIGHT_RESOLUTION", "0.10"))
WEIGHT_EXPOSURE = float(os.getenv("WEIGHT_EXPOSURE", "0.30"))
WEIGHT_FACE = float(os.getenv("WEIGHT_FACE", "0.25"))


# ---------------------------------------------------------------------------
# Category Thresholds
# ---------------------------------------------------------------------------
GOOD_THRESHOLD = float(os.getenv("GOOD_THRESHOLD", "70.0"))
REVIEW_THRESHOLD = float(os.getenv("REVIEW_THRESHOLD", "40.0"))
DUPLICATE_PENALTY = float(os.getenv("DUPLICATE_PENALTY", "10.0"))


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
MAX_ANALYSIS_DIMENSION = int(os.getenv("MAX_ANALYSIS_DIMENSION", "2048"))
THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", "300"))
PREVIEW_SIZE = int(os.getenv("PREVIEW_SIZE", "1200"))


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
