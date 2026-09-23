from pathlib import Path
from typing import Optional
from PIL import Image as PILImage
import imagehash
import hashlib

from app.config import DUPLICATE_HASH_SIZE
from app.utils.logger import logger

def calculate_hashes(filepath: str) -> dict:
    """
    Calculate perceptual (phash) and exact (md5) hashes for an image.
    
    Args:
        filepath: Path to the image file.
        
    Returns:
        dict: {
            "perceptual_hash": str or None,
            "exact_hash": str or None
        }
    """
    results = {
        "perceptual_hash": None,
        "exact_hash": None
    }
    
    try:
        # Calculate perceptual hash using imagehash
        with PILImage.open(filepath) as img:
            phash = imagehash.phash(img, hash_size=DUPLICATE_HASH_SIZE)
            results["perceptual_hash"] = str(phash)
            
        # Calculate exact hash (MD5) for identical files
        md5_hash = hashlib.md5()
        with open(filepath, "rb") as f:
            # Read in chunks to avoid memory issues with large files
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        results["exact_hash"] = md5_hash.hexdigest()
        
    except Exception as e:
        logger.error(f"Failed to calculate hashes for {filepath}: {e}")
        
    return results

def compute_similarity(hash1_str: str, hash2_str: str) -> int:
    """
    Compute the Hamming distance between two perceptual hashes.
    Lower distance means more similar (0 = identical perceptual hash).
    
    Args:
        hash1_str: String representation of imagehash
        hash2_str: String representation of imagehash
        
    Returns:
        int: Hamming distance, or 999 on error
    """
    try:
        if not hash1_str or not hash2_str:
            return 999
            
        h1 = imagehash.hex_to_hash(hash1_str)
        h2 = imagehash.hex_to_hash(hash2_str)
        
        return h1 - h2
    except Exception as e:
        logger.error(f"Failed to compute similarity: {e}")
        return 999
