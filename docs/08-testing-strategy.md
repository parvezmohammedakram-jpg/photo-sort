# PhotoSort -- Testing Strategy Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Testing Framework

| Tool | Purpose |
|------|---------|
| pytest | Test runner and assertion framework |
| pytest-cov | Code coverage reporting |
| httpx | Async HTTP client for API testing (works with FastAPI TestClient) |
| FastAPI TestClient | In-process API testing without starting a server |

---

## 2. Test Categories

### 2.1 Unit Tests

Test individual functions and analyzers in isolation. No database, no API, no file system dependencies beyond test fixtures.

### 2.2 Integration Tests

Test component interactions: API endpoints hitting the database, pipeline calling analyzers, export writing files.

### 2.3 End-to-End Tests

Test the full workflow from folder import to export, verifying data flows correctly through all layers.

---

## 3. Test Plan by Module

### 3.1 BlurAnalyzer Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| Sharp image | Programmatically generated sharp-edge image | sharpness_score > SHARP_THRESHOLD, status = "sharp" |
| Blurry image | Gaussian-blurred version of sharp image | sharpness_score < BORDERLINE_THRESHOLD, status = "blurry" |
| Borderline image | Mildly blurred image | BORDERLINE < score < SHARP, status = "borderline" |
| Invalid input | None / empty array | Raises appropriate exception or returns error result |
| Grayscale image | Already-grayscale image | Produces valid result without crash |

### 3.2 ResolutionAnalyzer Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| High resolution | 4000x3000 image | megapixels = 12.0, status = "acceptable" |
| Low resolution | 320x240 image | status = "low" |
| Minimum boundary | Image at exact MIN_WIDTH x MIN_HEIGHT | status = "acceptable" |
| Below minimum width | Image with width < MIN_WIDTH but height >= MIN_HEIGHT | status = "low" |
| Below minimum height | Image with height < MIN_HEIGHT but width >= MIN_WIDTH | status = "low" |

### 3.3 ExposureAnalyzer Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| Normal exposure | Balanced histogram image | exposure_status = "good" |
| Underexposed | Very dark image (mean brightness < 60) | exposure_status = "underexposed" |
| Overexposed | Very bright image (mean brightness > 200) | exposure_status = "overexposed" |
| Mixed exposure | Normal brightness with scattered distribution | exposure_status = "good" |
| Pure black | All-zero pixel image | exposure_status = "underexposed" |
| Pure white | All-255 pixel image | exposure_status = "overexposed" |

### 3.4 FaceAnalyzer Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| No face | Landscape/scenery image | face_count = 0, face_status = "no_face" |
| One face | Portrait with one clear face | face_count = 1, face_status = "faces_detected" |
| Multiple faces | Group photo | face_count > 1, face_status = "faces_detected" |
| Closed eyes | Face with clearly closed eyes | closed_eye_detected = True (if detection works) |
| Open eyes | Face with clearly open eyes | closed_eye_detected = False |
| Invalid input | Corrupted image data | face_status = "analysis_failed" (no crash) |

### 3.5 DuplicateAnalyzer Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| Exact duplicate | Two identical files | Grouped together, group_type = "exact" |
| Resized copy | Original + 50% scaled version | Grouped as near-duplicate |
| JPEG re-compressed | Same image saved at different quality | Grouped as near-duplicate |
| Unrelated images | Two completely different photos | Not grouped |
| Single image | Only one image in the set | No duplicate group |
| All identical | 5 copies of same file | All in one group |

### 3.6 Quality Scoring Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| Perfect scores | All metrics optimal | quality_score close to 100 |
| All poor | All metrics failing | quality_score close to 0 |
| Mixed quality | Some good, some bad metrics | Score in mid range |
| Duplicate penalty | Good scores but is a duplicate | Score reduced by duplicate penalty |
| Deterministic | Same inputs twice | Identical scores both times |

### 3.7 Classification Tests

| Test Case | Input | Expected |
|-----------|-------|----------|
| Above good threshold | score = 85 (threshold = 75) | category = "good" |
| Review range | score = 55 (good=75, review=40) | category = "review" |
| Below review threshold | score = 30 (review=40) | category = "poor" |
| Exact boundary (good) | score = 75 (threshold = 75) | category = "good" |
| Exact boundary (review) | score = 40 (threshold = 40) | category = "review" |

### 3.8 API Tests

| Test Case | Method | Endpoint | Expected |
|-----------|--------|----------|----------|
| Health check | GET | /api/health | 200, service info |
| Create project (valid path) | POST | /api/projects | 201, project created |
| Create project (invalid path) | POST | /api/projects | 400, error response |
| Create project (nonexistent path) | POST | /api/projects | 404, error response |
| Get project | GET | /api/projects/1 | 200, project data |
| Get nonexistent project | GET | /api/projects/999 | 404 |
| List photos | GET | /api/projects/1/photos | 200, paginated list |
| Get photo detail | GET | /api/photos/1 | 200, full photo data |
| Update category (valid) | PATCH | /api/photos/1/category | 200, updated |
| Update category (invalid value) | PATCH | /api/photos/1/category | 400 |
| Get statistics | GET | /api/projects/1/statistics | 200, aggregated counts |
| Get duplicates | GET | /api/projects/1/duplicates | 200, grouped duplicates |

### 3.9 Export Tests

| Test Case | Expected |
|-----------|----------|
| Export good photos | Files copied to output directory |
| Originals unchanged | Source files have same hash before and after export |
| Missing source file | Logged and skipped, export continues |
| Invalid output path | Error returned, no partial export |
| Empty selection | Error returned, no directory created |

---

## 4. Test Dataset

Create a small set of programmatically generated test images:

```
tests/test_images/
  sharp_high_res.jpg          # Generated: clear edges, 2000x1500
  blurry.jpg                  # Generated: Gaussian blur applied to sharp image
  borderline_blur.jpg         # Generated: mild blur
  underexposed.jpg            # Generated: dark image (brightness ~40)
  overexposed.jpg             # Generated: bright image (brightness ~230)
  normal_exposure.jpg         # Generated: balanced histogram
  low_resolution.jpg          # Generated: 200x150
  duplicate_a.jpg             # Copy of a test image
  duplicate_b.jpg             # Identical copy of duplicate_a
  near_duplicate.jpg          # Resized version of duplicate_a
  face_single.jpg             # Will need a real or generated face image
  no_face.jpg                 # Landscape/abstract image
  corrupted.jpg               # Intentionally corrupted file
  empty.jpg                   # Zero-byte file
```

Test images that require faces will use either:
- Generated geometric face approximations (for basic testing)
- Public domain face images (properly licensed)

No copyrighted or private photographs in the test dataset.

---

## 5. Test Generation Script

A setup script will generate synthetic test images:

```python
# scripts/generate_test_images.py

import cv2
import numpy as np

def generate_sharp_image(path, width=2000, height=1500):
    """Generate an image with clear edges (high Laplacian variance)."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Draw geometric shapes with sharp edges
    cv2.rectangle(img, (100, 100), (500, 500), (255, 255, 255), 2)
    cv2.circle(img, (1000, 750), 300, (128, 128, 128), 3)
    # Add noise for texture
    noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    cv2.imwrite(path, img)

def generate_blurry_image(sharp_path, output_path, kernel_size=51):
    """Apply heavy Gaussian blur to create a blurry test image."""
    img = cv2.imread(sharp_path)
    blurred = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    cv2.imwrite(output_path, blurred)
```

---

## 6. Coverage Target

| Module | Minimum Coverage |
|--------|-----------------|
| analyzers/ | 80% |
| services/scoring.py | 90% |
| services/classification.py | 90% |
| api/routes/ | 70% |
| Overall | 70% |

Coverage is a guide, not a goal. 70% overall with strong coverage on scoring and classification logic is more valuable than 95% coverage with trivial tests.

---

## 7. Accuracy Evaluation

For a labeled test set, calculate:

| Metric | Module | Method |
|--------|--------|--------|
| Accuracy | Blur Detection | % of correctly classified sharp/blurry on labeled set |
| Accuracy | Exposure | % of correctly classified under/normal/over on labeled set |
| Precision | Duplicate Detection | Of flagged duplicates, how many are actual duplicates |
| Recall | Duplicate Detection | Of actual duplicates, how many were flagged |
| Detection Rate | Face Detection | % of faces correctly found on images with known face counts |

**Honest reporting rules:**
- If the test dataset has fewer than 50 images per category, state that the sample size is too small for statistically significant claims
- Report the raw numbers (e.g., "14 of 16 blurry images correctly classified") alongside percentages
- Document any known failure modes
- Do not fabricate accuracy numbers

---

## 8. Running Tests

```bash
# Run all tests
cd backend
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Run specific module tests
python -m pytest tests/test_blur.py -v
python -m pytest tests/test_api.py -v
```
