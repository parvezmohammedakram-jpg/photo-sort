# PhotoSort -- Product Requirements Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft  
**Project Type:** BCA Final Year Project

---

## 1. Product Overview

PhotoSort is an automated photo quality detection and organization system. It processes collections of photographs, evaluates each image against multiple measurable quality parameters, assigns a numerical quality score, categorizes images into three tiers, and provides a review interface for manual adjustments and export.

The system targets photographers (wedding, event, studio), casual users (trips, family gatherings, burst photography), and anyone managing large photo libraries who needs to reduce the time spent manually culling unusable images.

---

## 2. Problem Statement

Large photo collections accumulate images with technical defects: blur, poor exposure, low resolution, closed eyes, and duplicates. Manual sorting is time-consuming, subjective, inconsistent, and prone to fatigue-induced errors. Existing gallery tools offer no quality-based filtering. There is no standardized, objective scoring mechanism for photo quality.

---

## 3. Functional Requirements

### FR-01: Image Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01.1 | Accept a local folder path containing photographs | Must |
| FR-01.2 | Discover all image files recursively within the folder | Must |
| FR-01.3 | Support JPG, JPEG, PNG, WEBP formats | Must |
| FR-01.4 | Skip unsupported file types without error | Must |
| FR-01.5 | Validate image integrity before processing | Must |
| FR-01.6 | Extract file metadata (size, dimensions, format, creation date) | Must |
| FR-01.7 | Store image metadata in the database | Must |
| FR-01.8 | Report count of found, supported, and skipped files | Must |

### FR-02: Blur Detection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-02.1 | Detect blurry/out-of-focus images using Laplacian variance | Must |
| FR-02.2 | Report a numeric sharpness score per image | Must |
| FR-02.3 | Classify blur status as Sharp, Borderline, or Blurry | Must |
| FR-02.4 | Use configurable thresholds from centralized config | Must |

### FR-03: Resolution Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-03.1 | Record width, height, and megapixel count | Must |
| FR-03.2 | Compare against minimum resolution thresholds | Must |
| FR-03.3 | Classify resolution as Acceptable or Low | Must |
| FR-03.4 | Minimum resolution thresholds must be configurable | Must |

### FR-04: Exposure Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-04.1 | Calculate average brightness from grayscale histogram | Must |
| FR-04.2 | Calculate dark-pixel percentage (pixels below threshold) | Must |
| FR-04.3 | Calculate bright-pixel percentage (pixels above threshold) | Must |
| FR-04.4 | Classify exposure as Underexposed, Good, or Overexposed | Must |
| FR-04.5 | Use multiple indicators, not brightness alone | Must |

### FR-05: Facial / Eye Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-05.1 | Detect faces in photographs | Must |
| FR-05.2 | Report face count per image | Must |
| FR-05.3 | Detect closed-eye conditions where technically feasible | Must |
| FR-05.4 | Handle zero, one, or multiple faces without crashing | Must |
| FR-05.5 | Architecture must allow future model upgrades | Must |
| FR-05.6 | Document limitations honestly (no fake confidence values) | Must |

### FR-06: Duplicate Detection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-06.1 | Detect exact duplicates using file hashing (MD5/SHA) | Must |
| FR-06.2 | Detect near-duplicates using perceptual hashing | Must |
| FR-06.3 | Group duplicates into named groups | Must |
| FR-06.4 | Report similarity percentage between near-duplicates | Must |
| FR-06.5 | Configurable similarity threshold | Must |
| FR-06.6 | Never auto-delete any photographs | Must |

### FR-07: Quality Scoring

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-07.1 | Calculate an overall quality score (0-100) per image | Must |
| FR-07.2 | Combine sharpness, resolution, exposure, facial, duplicate metrics | Must |
| FR-07.3 | Use documented, configurable weights per factor | Must |
| FR-07.4 | Scoring must be deterministic (same input = same score) | Must |
| FR-07.5 | Apply duplicate penalty to quality score | Must |

### FR-08: Categorization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-08.1 | Classify each image as Good/Select, Review, or Poor Quality | Must |
| FR-08.2 | Classification based on quality score thresholds | Must |
| FR-08.3 | Thresholds must be centralized and configurable | Must |

### FR-09: Manual Review

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-09.1 | Display quality score and all analysis metrics per image | Must |
| FR-09.2 | Allow manual category reassignment | Must |
| FR-09.3 | Track whether classification was manually modified | Must |
| FR-09.4 | Persist manual changes in the database | Must |

### FR-10: Export

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10.1 | Export Good/Select photos to an output directory | Must |
| FR-10.2 | Export by category (Good, Review, Poor separately) | Should |
| FR-10.3 | Copy files; never move or delete originals | Must |
| FR-10.4 | Report export progress and completion | Must |

### FR-11: Processing Pipeline

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-11.1 | Process images sequentially through all analyzers | Must |
| FR-11.2 | Continue batch on individual image failure | Must |
| FR-11.3 | Report real-time processing progress | Must |
| FR-11.4 | Log errors with sufficient debugging information | Must |

---

## 4. Non-Functional Requirements

### NFR-01: Performance

| ID | Requirement |
|----|-------------|
| NFR-01.1 | Process 100+ images without excessive memory consumption |
| NFR-01.2 | Resize images for analysis where full resolution is unnecessary |
| NFR-01.3 | Generate thumbnails for UI display |
| NFR-01.4 | Avoid loading entire collection into memory simultaneously |
| NFR-01.5 | Process images incrementally with result persistence |

### NFR-02: Reliability

| ID | Requirement |
|----|-------------|
| NFR-02.1 | Single corrupted image must not crash the batch |
| NFR-02.2 | Handle permission errors, missing files, invalid paths |
| NFR-02.3 | Handle extremely large images without memory exhaustion |
| NFR-02.4 | Log errors at appropriate severity levels |

### NFR-03: Security

| ID | Requirement |
|----|-------------|
| NFR-03.1 | Validate file paths to prevent directory traversal |
| NFR-03.2 | Sanitize filenames |
| NFR-03.3 | Enforce file size limits |
| NFR-03.4 | Reject invalid file types at upload validation |

### NFR-04: Usability

| ID | Requirement |
|----|-------------|
| NFR-04.1 | Interface understandable by non-technical users |
| NFR-04.2 | Show human-readable status labels (not raw metric values) |
| NFR-04.3 | Advanced metrics available in detail view |
| NFR-04.4 | Clear communication of processing state at all times |

### NFR-05: Maintainability

| ID | Requirement |
|----|-------------|
| NFR-05.1 | Modular architecture with separated concerns |
| NFR-05.2 | Centralized configuration for all thresholds |
| NFR-05.3 | Analysis modules replaceable/upgradable independently |
| NFR-05.4 | Clean Python with type hints and documentation |

---

## 5. Original File Safety Constraint

PhotoSort must NEVER modify, rename, move, or delete original photographs by default. The entire workflow is:

```
READ ORIGINAL --> ANALYZE --> STORE METADATA --> COPY ON EXPORT
```

Destructive operations require explicit user action and are not part of Version 1.

---

## 6. Out of Scope (Version 1)

- RAW image format support
- Cloud deployment
- Cloud storage integration (Google Drive, Dropbox)
- Mobile application
- Automatic file renaming/tagging
- AI-based enhancement suggestions
- Deep learning aesthetic quality scoring
- User authentication/multi-user support

These items are documented as future scope per the project synopsis.

---

## 7. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Automated analysis | All 5 analysis modules produce real, verifiable results |
| Quality scoring | Every processed image receives a deterministic score |
| Categorization | Images correctly classified based on configured thresholds |
| Error resilience | Corrupted/invalid images logged and skipped, batch continues |
| Export safety | Original files remain untouched after export |
| Time reduction | Estimated 60-80% reduction in manual culling time (evaluated, not guaranteed) |
| Accuracy | Measured against a labeled test dataset with documented methodology |
