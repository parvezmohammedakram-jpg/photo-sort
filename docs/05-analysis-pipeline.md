# PhotoSort -- Analysis Pipeline Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Pipeline Overview

The analysis pipeline is the core processing engine. It takes a folder of images and produces quality scores, categories, and duplicate groups. Each step is independent and failure-isolated.

```
FOLDER PATH
     |
     v
[1] FILE DISCOVERY
     |  Scan folder, filter by extension, count files
     v
[2] FILE VALIDATION
     |  Check integrity, read metadata, reject corrupted files
     v
[3] IMAGE LOADING (per image)
     |  Load with OpenCV, resize for analysis if > threshold
     v
[4] BLUR ANALYSIS
     |  Laplacian variance on grayscale
     v
[5] RESOLUTION ANALYSIS
     |  Dimensions and megapixel calculation
     v
[6] EXPOSURE ANALYSIS
     |  Histogram-based brightness and pixel distribution
     v
[7] FACIAL / EYE ANALYSIS
     |  MediaPipe face detection + eye landmark analysis
     v
[8] THUMBNAIL GENERATION
     |  Create 300px and 1200px resized copies
     v
[9] STORE INDIVIDUAL RESULTS
     |  Persist photo + analysis records to database
     v
--- After all images processed ---
     |
[10] DUPLICATE ANALYSIS
     |  Compare hashes across all images, form groups
     v
[11] QUALITY SCORING
     |  Combine all metrics into 0-100 score
     v
[12] CLASSIFICATION
     |  Assign Good / Review / Poor based on score thresholds
     v
[13] FINAL PERSISTENCE
     |  Update scores, categories, duplicate groups in database
```

---

## 2. Analyzer Interface

Every analyzer implements the same abstract interface:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import numpy as np


class AnalyzerResult:
    """Base class for analyzer results."""
    pass


class BaseAnalyzer(ABC):
    """Abstract base for all image analyzers."""

    @abstractmethod
    def analyze(self, image: np.ndarray, filepath: str = None) -> AnalyzerResult:
        """
        Analyze an image and return structured results.

        Args:
            image: BGR image as NumPy array (loaded by cv2)
            filepath: Optional original file path for metadata

        Returns:
            AnalyzerResult subclass with analysis metrics
        """
        pass
```

This ensures all analyzers are interchangeable and testable in isolation.

---

## 3. Analyzer Specifications

### 3.1 BlurAnalyzer

**Purpose:** Detect blurry or out-of-focus photographs.

**Algorithm: Laplacian Variance**

```
1. Convert image to grayscale
2. Apply Laplacian operator (second derivative)
3. Calculate variance of the Laplacian output
4. Higher variance = more edges = sharper image
5. Lower variance = fewer edges = blurrier image
```

**Why Laplacian variance:** It measures the rate of intensity change in an image. Sharp images have strong edges (high variance). Blurry images have smooth transitions (low variance). It is computationally cheap, well-documented in OpenCV, and provides a single numeric value that is easy to threshold.

**Output:**

```python
@dataclass
class BlurResult(AnalyzerResult):
    sharpness_score: float      # Laplacian variance value
    blur_status: str            # "sharp", "borderline", "blurry"
```

**Thresholds (configurable):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| BLUR_SHARP_THRESHOLD | 100.0 | Above this = sharp |
| BLUR_BORDERLINE_THRESHOLD | 50.0 | Above this but below sharp = borderline |
| Below borderline | -- | Blurry |

**Note:** These defaults are initial estimates. They must be calibrated against sample images during Phase 3.

---

### 3.2 ResolutionAnalyzer

**Purpose:** Flag images below minimum acceptable resolution.

**Algorithm:**

```
1. Read image dimensions (width, height) from the loaded array
2. Calculate megapixels = (width * height) / 1,000,000
3. Compare against minimum width, height, and megapixel thresholds
```

**Output:**

```python
@dataclass
class ResolutionResult(AnalyzerResult):
    width: int
    height: int
    megapixels: float
    resolution_status: str      # "acceptable", "low"
```

**Thresholds (configurable):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| MIN_WIDTH | 1280 | Minimum acceptable width in pixels |
| MIN_HEIGHT | 720 | Minimum acceptable height in pixels |
| MIN_MEGAPIXELS | 1.0 | Minimum acceptable megapixels |

---

### 3.3 ExposureAnalyzer

**Purpose:** Detect underexposed and overexposed photographs.

**Algorithm:**

```
1. Convert to grayscale
2. Calculate histogram (256 bins)
3. Calculate average brightness = mean of all pixel values
4. Calculate dark_pixel_pct = percentage of pixels below dark threshold (e.g., 30)
5. Calculate bright_pixel_pct = percentage of pixels above bright threshold (e.g., 225)
6. Classify based on multiple indicators:
   - If average brightness < low_threshold AND dark_pixel_pct > 40%: underexposed
   - If average brightness > high_threshold AND bright_pixel_pct > 40%: overexposed
   - Otherwise: good
```

**Why multiple indicators:** Average brightness alone is unreliable. A photo with a bright sky and dark foreground might have acceptable average brightness but still be poorly exposed. Combining average brightness with pixel distribution provides a more robust assessment.

**Output:**

```python
@dataclass
class ExposureResult(AnalyzerResult):
    brightness_avg: float       # Mean brightness (0-255)
    dark_pixel_pct: float       # Percentage of dark pixels
    bright_pixel_pct: float     # Percentage of bright pixels
    exposure_status: str        # "underexposed", "good", "overexposed"
```

**Thresholds (configurable):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| EXPOSURE_LOW_BRIGHTNESS | 60 | Below this average = dark |
| EXPOSURE_HIGH_BRIGHTNESS | 200 | Above this average = bright |
| DARK_PIXEL_THRESHOLD | 30 | Pixel value below which a pixel is "dark" |
| BRIGHT_PIXEL_THRESHOLD | 225 | Pixel value above which a pixel is "bright" |
| DARK_PIXEL_PCT_THRESHOLD | 40.0 | Percentage of dark pixels to flag underexposure |
| BRIGHT_PIXEL_PCT_THRESHOLD | 40.0 | Percentage of bright pixels to flag overexposure |

---

### 3.4 FaceAnalyzer

**Purpose:** Detect faces and identify closed-eye conditions.

**Algorithm:**

```
1. Use MediaPipe Face Detection to locate faces in the image
2. For each detected face:
   a. Use MediaPipe Face Mesh to locate eye landmarks
   b. Calculate Eye Aspect Ratio (EAR) from landmark positions
   c. EAR below threshold indicates closed eyes
3. Report face count and closed-eye status
```

**Eye Aspect Ratio (EAR):**

```
EAR = (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)

Where p1-p6 are the six eye landmark points.

Open eye: EAR approximately 0.25-0.35
Closed eye: EAR approximately 0.1-0.15
```

**Why MediaPipe:** Lightweight, runs on CPU, provides both face detection and 468 facial landmarks (including detailed eye landmarks) without requiring a GPU or heavy model files. Suitable for a college project.

**Output:**

```python
@dataclass
class FaceResult(AnalyzerResult):
    face_count: int             # Number of detected faces
    closed_eye_detected: bool   # Any face has closed eyes
    face_status: str            # "no_face", "faces_detected",
                                # "closed_eyes_detected", "analysis_failed"
    face_details: list          # Per-face details (optional)
```

**Known Limitations (documented honestly):**

- Face detection accuracy drops on partially visible, rotated, or very small faces
- Eye aspect ratio may be unreliable on faces far from the camera
- No "poor expression" detection; the system only detects closed/open eyes
- False positives possible on very low-resolution face crops
- MediaPipe requires the face to be reasonably visible and front-facing

**Thresholds (configurable):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| FACE_DETECTION_CONFIDENCE | 0.5 | Minimum confidence for face detection |
| EYE_CLOSED_THRESHOLD | 0.18 | EAR below this = eye is closed |

---

### 3.5 DuplicateAnalyzer

**Purpose:** Identify exact and near-duplicate photographs.

**Algorithm:**

```
Phase 1: Exact Duplicates
  1. Calculate MD5 hash of each file's content
  2. Group files with identical hashes

Phase 2: Near-Duplicates
  1. Calculate perceptual hash (average hash or difference hash) for each image
  2. Compare hashes between images using Hamming distance
  3. Hamming distance below threshold = near-duplicate
  4. Group near-duplicates

Optimization:
  - Only compare images against others within the same project
  - Skip comparisons between images already in the same exact-duplicate group
  - Use sorted hash comparison to reduce O(n^2) to practical levels
```

**Why perceptual hashing:** Traditional cryptographic hashes (MD5) detect only byte-identical files. Perceptual hashes produce similar values for visually similar images, catching resized, re-compressed, or slightly cropped duplicates. The `imagehash` Python library provides multiple perceptual hashing algorithms.

**Output:**

```python
@dataclass
class DuplicateResult(AnalyzerResult):
    file_hash: str              # MD5 hash for exact matching
    perceptual_hash: str        # Perceptual hash for similarity
    # Grouping is done at the pipeline level, not per-image
```

**Thresholds (configurable):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| DUPLICATE_HASH_THRESHOLD | 10 | Hamming distance below this = near-duplicate |
| DUPLICATE_HASH_SIZE | 16 | Hash size for perceptual hashing (higher = more precise) |

---

## 4. Image Loading Strategy

To handle large images without exhausting memory:

```
1. Load image with cv2.imread()
2. If image dimensions exceed MAX_ANALYSIS_DIMENSION (e.g., 2048px):
   a. Calculate scale factor
   b. Resize image for analysis
   c. Original dimensions still recorded for resolution analysis
3. Generate thumbnail (300px max) for UI
4. Generate preview (1200px max) for detail view
5. Release the full-resolution array from memory
```

The original file is never modified. Analysis images are resized copies held only in memory during processing.

---

## 5. Error Isolation

Each image is processed inside a try/except block:

```python
for photo in photos:
    try:
        image = load_image(photo.filepath)
        blur_result = blur_analyzer.analyze(image)
        resolution_result = resolution_analyzer.analyze(image)
        exposure_result = exposure_analyzer.analyze(image)
        face_result = face_analyzer.analyze(image)
        # Store results
        photo.status = "completed"
    except Exception as e:
        logger.error(f"Failed to process {photo.filename}: {e}")
        photo.status = "failed"
        photo.error_message = str(e)
        # Continue to next image
```

Individual analyzer failures within a single image can also be isolated:

```python
try:
    face_result = face_analyzer.analyze(image)
except Exception as e:
    face_result = FaceResult(
        face_count=0,
        closed_eye_detected=False,
        face_status="analysis_failed"
    )
    logger.warning(f"Face analysis failed for {photo.filename}: {e}")
```

This ensures that a face detection failure does not prevent blur, resolution, and exposure results from being recorded.
