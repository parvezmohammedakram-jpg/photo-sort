"""
File utility functions.

Path validation, extension checking, filename sanitization.
"""

import os
import re
from pathlib import Path
from typing import Optional

from app.config import SUPPORTED_EXTENSIONS


def is_supported_extension(filepath: str) -> bool:
    """Check if a file has a supported image extension."""
    ext = Path(filepath).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """
    Remove potentially unsafe characters from a filename.
    Preserves the extension and alphanumeric characters.
    """
    name = Path(filename).stem
    ext = Path(filename).suffix.lower()
    # Keep alphanumeric, hyphens, underscores, dots, and spaces
    safe_name = re.sub(r'[^\w\s\-.]', '', name).strip()
    if not safe_name:
        safe_name = "unnamed"
    return safe_name + ext


def validate_directory_path(path: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a path is a real, accessible directory.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not path or not path.strip():
        return False, "Path is empty"

    clean_path = path.strip().strip('"').strip("'")
    resolved = Path(clean_path).resolve()

    if not resolved.exists():
        return False, f"Path does not exist: {resolved}"

    if not resolved.is_dir():
        return False, f"Path is not a directory: {resolved}"

    # Check read permission
    if not os.access(resolved, os.R_OK):
        return False, f"No read permission for: {resolved}"

    return True, None


def validate_output_path(path: str) -> tuple[bool, Optional[str]]:
    """
    Validate that an output path can be created and written to.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not path or not path.strip():
        return False, "Output path is empty"

    clean_path = path.strip().strip('"').strip("'")
    resolved = Path(clean_path).resolve()

    # Check that parent directory exists and is writable
    parent = resolved.parent
    if not parent.exists():
        return False, f"Parent directory does not exist: {parent}"

    if not os.access(parent, os.W_OK):
        return False, f"No write permission for: {parent}"

    return True, None


def discover_images(directory: str) -> tuple[list[Path], list[Path]]:
    """
    Scan a directory for image files.

    Args:
        directory: Path to the directory to scan.

    Returns:
        Tuple of (supported_files, skipped_files).
    """
    supported = []
    skipped = []

    dir_path = Path(directory).resolve()

    for item in sorted(dir_path.rglob("*")):
        if item.is_file():
            if is_supported_extension(str(item)):
                supported.append(item)
            else:
                skipped.append(item)

    return supported, skipped
