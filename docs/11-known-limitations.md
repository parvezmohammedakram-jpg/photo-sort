# PhotoSort -- Known Limitations Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Overview

This document honestly identifies the known limitations of PhotoSort. These limitations are inherent to the chosen approach, the available technology, or the scope of a college project. They are documented here for academic transparency and to guide future development.

---

## 2. Image Analysis Limitations

### 2.1 Blur Detection

| Limitation | Explanation |
|------------|-------------|
| Motion blur vs. defocus | Laplacian variance does not distinguish between motion blur and optical defocus. Both produce low variance scores. |
| Intentional blur | Artistic bokeh (shallow depth of field) may be incorrectly flagged as blurry. The background blur in portrait mode is a feature, not a defect. |
| Textured blur | A blurry image of a highly textured surface (e.g., carpet, fabric) may have higher variance than a sharp image of a smooth surface. |
| Edge cases | Very dark or very bright images produce unreliable Laplacian variance values because contrast is insufficient for edge detection. |

### 2.2 Exposure Analysis

| Limitation | Explanation |
|------------|-------------|
| High-dynamic-range scenes | A photo with both very bright and very dark regions (e.g., sunset, backlit subject) may have acceptable average brightness but still be poorly exposed for the subject. |
| Histogram shape | The system uses average brightness and pixel percentages but does not analyze histogram modality or distribution shape. A bimodal histogram indicates HDR issues that average brightness misses. |
| Artistic intent | Silhouettes, low-key photography, and high-key photography are valid artistic choices that may be flagged as exposure problems. |
| Color vs. luminance | The system converts to grayscale for brightness analysis. Color channel imbalances (e.g., strong color cast) are not detected. |

### 2.3 Face Detection

| Limitation | Explanation |
|------------|-------------|
| MediaPipe accuracy | MediaPipe Face Detection works well for frontal, well-lit faces but accuracy degrades for: profile views (>30 degrees), small faces (<64px), partial occlusion, strong backlighting, extreme expressions. |
| Eye state detection | Eye Aspect Ratio is an approximation. It may produce false positives on: squinting eyes, very small faces, faces at angles, people with naturally narrow eyes. |
| No expression analysis | The system cannot detect "poor facial expressions" as described in the synopsis. Only eye open/closed state is assessed. Expression analysis would require a deep learning model that is beyond the current scope. |
| Multiple faces | When multiple faces are detected, closed eyes on any face flags the entire image. The system does not identify which specific face has closed eyes in the current output. |
| False negatives | Faces covered by masks, sunglasses, or heavy makeup may not be detected. The system reports "no face" in these cases. |

### 2.4 Duplicate Detection

| Limitation | Explanation |
|------------|-------------|
| Perceptual hash threshold | The similarity threshold is a trade-off between precision and recall. A low threshold catches more near-duplicates but may produce false positives (grouping images that are merely similar in color). |
| Performance on large sets | Pairwise comparison is O(n^2). For collections above ~5000 images, comparison time becomes significant. Optimization (e.g., locality-sensitive hashing, VP-trees) is deferred to future scope. |
| Content-similar vs. duplicate | Two photos of the same scene from slightly different angles are "similar" but not "duplicates." The system cannot distinguish between near-duplicates (same shot, different compression) and content-similar (different shots of the same subject). |
| Cropped duplicates | Significant cropping changes the perceptual hash substantially. A tightly cropped version of a photo may not be detected as a near-duplicate. |

---

## 3. Scoring Limitations

| Limitation | Explanation |
|------------|-------------|
| Linear weighted model | The scoring model is a simple weighted sum. It does not capture non-linear interactions between quality factors (e.g., a slightly blurry portrait with great exposure vs. a sharp but badly exposed landscape). |
| No aesthetic assessment | "Good photograph" is subjective. The system measures technical quality only: sharpness, resolution, exposure, face/eyes, duplicates. Composition, color harmony, emotional impact, and artistic intent are not evaluated. |
| Weight sensitivity | The relative weights significantly affect scoring outcomes. Different photography contexts (events, landscapes, portraits, products) may benefit from different weight configurations. |
| Face-dependent bias | The default face weight (25%) may over-penalize landscape and object photography that contains no faces. Users should adjust weights based on their content type. |

---

## 4. Architecture Limitations

| Limitation | Explanation |
|------------|-------------|
| Single-user, local only | PhotoSort is designed as a single-user desktop application. It does not support concurrent users, remote access, or cloud deployment in Version 1. |
| SQLite constraints | SQLite handles concurrent writes poorly. If background processing and user interactions generate simultaneous writes, occasional locking may occur. For typical use (one processing pipeline at a time), this is not a problem. |
| No incremental re-analysis | Re-processing a folder re-analyzes all images, even those already processed. Incremental analysis (only new/changed files) is a future optimization. |
| Memory on very large images | Images above 50 megapixels may consume significant memory during loading. The resizing strategy mitigates this, but extremely large panoramas or medium-format captures may still cause issues. |

---

## 5. Frontend Limitations

| Limitation | Explanation |
|------------|-------------|
| Folder path input | The web frontend cannot directly access the local file system. Folder selection relies on the user typing/pasting a path. Native folder picker requires Electron or a desktop wrapper. |
| No real-time streaming | Processing progress uses polling (every 2 seconds), not WebSocket streaming. There is a small delay between actual progress and displayed progress. |
| No image comparison view | Side-by-side comparison of two images (useful for duplicate review) is not implemented in Version 1. |

---

## 6. Accuracy Limitations

| Limitation | Explanation |
|------------|-------------|
| Small test dataset | The project test dataset is small (fewer than 50 images per category). Statistical claims about accuracy are limited. Results are reported as raw counts alongside percentages. |
| No industry benchmark | PhotoSort is not benchmarked against established image quality assessment (IQA) databases like LIVE, TID2013, or KADID-10k. Comparison with academic benchmarks is beyond project scope. |
| Threshold calibration | Default thresholds are calibrated against a limited sample. Different camera models, lighting conditions, and photographic styles may require threshold adjustment. |

---

## 7. Security Limitations

| Limitation | Explanation |
|------------|-------------|
| No authentication | PhotoSort has no login, no user accounts, no access control. It is intended as a local desktop tool. |
| Path traversal mitigation | Basic path validation is implemented, but the system inherently trusts the local user. A deliberately malicious user with local access could potentially exploit path handling. |
| No encryption | Analysis results and metadata are stored in plaintext SQLite. No encryption at rest. |

---

## 8. Future Scope Items (Not Limitations, but Not Implemented)

These items are explicitly deferred per the project synopsis:

- RAW image format support (CR2, NEF, ARW, DNG)
- Deep learning aesthetic quality scoring
- Cloud deployment
- Cloud storage integration (Google Drive, Dropbox)
- Mobile application
- Automatic file renaming and tagging
- AI-based enhancement suggestions
- Multi-user support
- GPU acceleration for analysis

---

## 9. Mitigation Strategies

For the limitations that users are most likely to encounter:

| Limitation | Mitigation |
|------------|------------|
| Bokeh flagged as blurry | User can manually reclassify the photo from the detail view |
| Artistic exposure flagged | User can adjust exposure thresholds in configuration or manually reclassify |
| False positive face detection | User can check detection in detail view and reclassify |
| Large collection performance | Process in smaller batches; future versions can add optimization |
| Weight configuration | Scoring weights are documented and configurable; user can adjust for their content type |
