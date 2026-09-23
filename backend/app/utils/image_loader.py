"""
Safe image loading and validation.

Handles corrupted files, oversized images, and format issues
without crashing the application.
"""

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image as PILImage

from app.config import MAX_ANALYSIS_DIMENSION, THUMBNAIL_SIZE, PREVIEW_SIZE
from app.utils.logger import logger


def load_image(filepath: str) -> Optional[np.ndarray]:
    """
    Load an image file safely using OpenCV.

    Args:
        filepath: Absolute path to the image file.

    Returns:
        BGR image as NumPy array, or None if loading fails.
    """
    try:
        image = cv2.imread(filepath)
        if image is None:
            logger.warning(f"OpenCV could not read image: {filepath}")
            return None
        return image
    except Exception as e:
        logger.error(f"Failed to load image {filepath}: {e}")
        return None


def resize_for_analysis(image: np.ndarray) -> np.ndarray:
    """
    Resize an image if it exceeds the maximum analysis dimension.
    Maintains aspect ratio.

    Args:
        image: BGR image array.

    Returns:
        Resized image (or original if within limits).
    """
    h, w = image.shape[:2]
    max_dim = max(h, w)

    if max_dim <= MAX_ANALYSIS_DIMENSION:
        return image

    scale = MAX_ANALYSIS_DIMENSION / max_dim
    new_w = int(w * scale)
    new_h = int(h * scale)

    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def get_image_dimensions(filepath: str) -> Optional[tuple[int, int]]:
    """
    Get image dimensions without loading the full image into memory.
    Uses PIL which reads only the header.

    Args:
        filepath: Path to the image file.

    Returns:
        Tuple of (width, height) or None if the file cannot be read.
    """
    try:
        with PILImage.open(filepath) as img:
            return img.size  # (width, height)
    except Exception as e:
        logger.warning(f"Could not read dimensions for {filepath}: {e}")
        return None


def validate_image(filepath: str) -> tuple[bool, Optional[str]]:
    """
    Check whether a file is a valid, readable image.

    Returns:
        Tuple of (is_valid, error_message).
    """
    path = Path(filepath)

    if not path.exists():
        return False, "File does not exist"

    if path.stat().st_size == 0:
        return False, "File is empty (0 bytes)"

    try:
        with PILImage.open(filepath) as img:
            img.verify()
        return True, None
    except Exception as e:
        return False, f"Image validation failed: {e}"


def generate_thumbnail(
    filepath: str, output_path: str, size: int = THUMBNAIL_SIZE
) -> Optional[str]:
    """
    Generate a JPEG thumbnail of the image.

    Args:
        filepath: Path to the source image.
        output_path: Path to save the thumbnail.
        size: Maximum dimension (width or height).

    Returns:
        Path to the generated thumbnail, or None on failure.
    """
    try:
        with PILImage.open(filepath) as img:
            img.thumbnail((size, size), PILImage.Resampling.LANCZOS)
            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if img.mode not in ("RGB",):
                img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=85)
            return output_path
    except Exception as e:
        logger.warning(f"Failed to generate thumbnail for {filepath}: {e}")
        return None


def generate_preview(
    filepath: str, output_path: str, size: int = PREVIEW_SIZE
) -> Optional[str]:
    """
    Generate a larger JPEG preview of the image.

    Args:
        filepath: Path to the source image.
        output_path: Path to save the preview.
        size: Maximum dimension.

    Returns:
        Path to the generated preview, or None on failure.
    """
    return generate_thumbnail(filepath, output_path, size=size)
