# PhotoSort -- System Architecture Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Architecture Overview

PhotoSort follows a modular monolithic architecture with clear separation between the backend API, the analysis engine, and the frontend interface. This is appropriate for a college project: simple to deploy, easy to debug, and sufficient for the expected scale (hundreds to low thousands of images per session).

```
+------------------+          +-------------------+          +-----------------+
|                  |   HTTP   |                   |          |                 |
|   React Frontend | -------> |   FastAPI Backend  | -------> |   SQLite DB     |
|                  |          |                   |          |                 |
+------------------+          +--------+----------+          +-----------------+
                                       |
                                       v
                              +--------+----------+
                              |                   |
                              |  Analysis Engine   |
                              |                   |
                              |  +-------------+  |
                              |  | BlurAnalyzer |  |
                              |  +-------------+  |
                              |  | ResAnalyzer  |  |
                              |  +-------------+  |
                              |  | ExpoAnalyzer |  |
                              |  +-------------+  |
                              |  | FaceAnalyzer |  |
                              |  +-------------+  |
                              |  | DupAnalyzer  |  |
                              |  +-------------+  |
                              |  | QualityScore |  |
                              |  +-------------+  |
                              +-------------------+
```

---

## 2. Component Responsibilities

### 2.1 Frontend (React)

- User interface for folder selection, processing status, results browsing, detail view, duplicate review, manual reclassification, and export.
- Communicates with backend exclusively through REST API.
- No direct file system access.
- Renders thumbnails served by the backend.

### 2.2 Backend (FastAPI)

- REST API layer handling all client requests.
- Project and session management.
- File discovery and validation.
- Orchestrates the processing pipeline.
- Serves thumbnails and image previews.
- Manages database operations.
- Export file copying logic.

### 2.3 Analysis Engine

- Independent analyzer modules, each implementing a common interface.
- Each analyzer receives an image (as a NumPy array or file path) and returns a structured result.
- Analyzers have no knowledge of the database, API, or frontend.
- The pipeline coordinator calls each analyzer in sequence and aggregates results.

### 2.4 Database (SQLite)

- Stores image metadata, analysis results, manual review state, and duplicate groups.
- Does NOT store image binary data.
- Single-file database, easy to back up and reset.

---

## 3. Directory Structure

```
photosort/
|
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- main.py                  # FastAPI application entry point
|   |   |-- config.py                # Centralized configuration
|   |   |-- database.py              # Database connection and session management
|   |   |
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- photo.py             # Photo ORM model
|   |   |   |-- analysis.py          # Analysis ORM model
|   |   |   |-- review.py            # Manual review ORM model
|   |   |   |-- project.py           # Project/session ORM model
|   |   |
|   |   |-- schemas/
|   |   |   |-- __init__.py
|   |   |   |-- photo.py             # Pydantic request/response schemas
|   |   |   |-- analysis.py
|   |   |   |-- project.py
|   |   |
|   |   |-- api/
|   |   |   |-- __init__.py
|   |   |   |-- routes/
|   |   |   |   |-- __init__.py
|   |   |   |   |-- projects.py      # Project endpoints
|   |   |   |   |-- photos.py        # Photo endpoints
|   |   |   |   |-- processing.py    # Processing endpoints
|   |   |   |   |-- duplicates.py    # Duplicate endpoints
|   |   |   |   |-- export.py        # Export endpoints
|   |   |   |   |-- health.py        # Health check endpoint
|   |   |
|   |   |-- services/
|   |   |   |-- __init__.py
|   |   |   |-- ingestion.py         # File discovery and validation
|   |   |   |-- pipeline.py          # Processing pipeline orchestrator
|   |   |   |-- scoring.py           # Quality score calculation
|   |   |   |-- classification.py    # Category assignment
|   |   |   |-- export.py            # Export file copying
|   |   |   |-- thumbnail.py         # Thumbnail generation
|   |   |
|   |   |-- analyzers/
|   |   |   |-- __init__.py
|   |   |   |-- base.py              # Abstract base analyzer
|   |   |   |-- blur.py              # Blur detection (Laplacian variance)
|   |   |   |-- resolution.py        # Resolution check
|   |   |   |-- exposure.py          # Exposure analysis (histogram)
|   |   |   |-- face.py              # Facial / eye detection
|   |   |   |-- duplicate.py         # Duplicate / near-duplicate detection
|   |   |
|   |   |-- utils/
|   |       |-- __init__.py
|   |       |-- image_loader.py      # Safe image loading and validation
|   |       |-- file_utils.py        # Path sanitization, extension checks
|   |       |-- logger.py            # Logging configuration
|   |
|   |-- tests/
|   |   |-- __init__.py
|   |   |-- conftest.py              # Shared fixtures
|   |   |-- test_blur.py
|   |   |-- test_resolution.py
|   |   |-- test_exposure.py
|   |   |-- test_face.py
|   |   |-- test_duplicate.py
|   |   |-- test_scoring.py
|   |   |-- test_classification.py
|   |   |-- test_api.py
|   |   |-- test_export.py
|   |   |-- test_images/             # Small test dataset
|   |
|   |-- requirements.txt
|   |-- .env.example
|   |-- alembic.ini                  # Optional: migrations
|
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- components/
|   |   |   |-- layout/
|   |   |   |   |-- Sidebar.jsx
|   |   |   |   |-- Header.jsx
|   |   |   |   |-- Layout.jsx
|   |   |   |-- dashboard/
|   |   |   |   |-- StatCard.jsx
|   |   |   |   |-- Dashboard.jsx
|   |   |   |-- photos/
|   |   |   |   |-- PhotoGrid.jsx
|   |   |   |   |-- PhotoCard.jsx
|   |   |   |   |-- PhotoDetail.jsx
|   |   |   |   |-- CategoryFilter.jsx
|   |   |   |-- processing/
|   |   |   |   |-- ProcessingView.jsx
|   |   |   |   |-- ProgressBar.jsx
|   |   |   |-- duplicates/
|   |   |   |   |-- DuplicateGroups.jsx
|   |   |   |   |-- DuplicateCard.jsx
|   |   |   |-- import/
|   |   |   |   |-- ImportView.jsx
|   |   |   |-- export/
|   |   |   |   |-- ExportView.jsx
|   |   |   |-- common/
|   |   |       |-- Button.jsx
|   |   |       |-- Badge.jsx
|   |   |       |-- Modal.jsx
|   |   |       |-- Tooltip.jsx
|   |   |-- hooks/
|   |   |   |-- useApi.js
|   |   |   |-- usePolling.js
|   |   |-- services/
|   |   |   |-- api.js               # API client
|   |   |-- styles/
|   |   |   |-- index.css            # Design system tokens and base styles
|   |   |   |-- variables.css        # CSS custom properties
|   |   |-- App.jsx
|   |   |-- main.jsx
|   |-- index.html
|   |-- package.json
|   |-- vite.config.js
|
|-- docs/
|   |-- 01-product-requirements.md
|   |-- 02-system-architecture.md
|   |-- 03-database-schema.md
|   |-- 04-api-contracts.md
|   |-- 05-analysis-pipeline.md
|   |-- 06-frontend-specification.md
|   |-- 07-development-phases.md
|   |-- 08-testing-strategy.md
|   |-- 09-ui-design-system.md
|   |-- 10-scoring-engine.md
|   |-- 11-known-limitations.md
|   |-- 12-installation-guide.md
|
|-- data/                            # Runtime data (thumbnails, db)
|-- exports/                         # Export output directory
|-- scripts/                         # Utility scripts
|-- README.md
|-- .gitignore
```

---

## 4. Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Backend Framework | FastAPI | Async-capable, automatic OpenAPI docs, Pydantic validation, lightweight |
| Image Processing | OpenCV (cv2) | Industry standard for computer vision, Laplacian variance, histogram analysis |
| Image Utilities | Pillow (PIL) | EXIF extraction, format validation, thumbnail generation |
| Numerical | NumPy | Required by OpenCV, used for array operations and statistical calculations |
| Face Detection | MediaPipe | Lightweight, no GPU required, includes face detection and face mesh (eye landmarks) |
| Database | SQLite via SQLAlchemy | Zero-config, single-file, sufficient for local application |
| ORM | SQLAlchemy | Python standard, type-safe queries, migration support |
| Frontend | React (Vite) | Component-based, fast dev server, widely understood |
| HTTP Client | Fetch API / Axios | Standard browser HTTP |
| Hashing | imagehash (Python) | Perceptual hashing library (average hash, difference hash, perceptual hash) |
| File Hashing | hashlib (stdlib) | MD5/SHA256 for exact duplicate detection |

### Why NOT these alternatives

| Rejected | Reason |
|----------|--------|
| Django | Heavier than needed for a REST API serving a React frontend |
| Flask | Less built-in validation, no automatic docs, no native async |
| TensorFlow/PyTorch | Heavyweight ML frameworks unnecessary when MediaPipe provides pre-trained face models |
| MongoDB | Overkill; SQLite is simpler and appropriate for single-user desktop use |
| Kubernetes/Redis | Overengineering for a college project |

---

## 5. Data Flow

```
User selects folder
       |
       v
[POST /api/projects] --> Create project record in DB
       |
       v
[POST /api/process/{project_id}] --> Start processing pipeline
       |
       v
File Discovery --> Scan folder for supported image files
       |
       v
Validation --> Check file integrity, extract metadata
       |
       v
For each valid image:
  |
  +---> Load image (resize for analysis if large)
  |
  +---> BlurAnalyzer.analyze(image)     --> sharpness_score, blur_status
  +---> ResolutionAnalyzer.analyze(image) --> width, height, megapixels, resolution_status
  +---> ExposureAnalyzer.analyze(image)  --> brightness, dark_pct, bright_pct, exposure_status
  +---> FaceAnalyzer.analyze(image)      --> face_count, closed_eye_detected, face_status
  |
  +---> Generate thumbnail
  +---> Store photo record + analysis record in DB
  |
  v
After all images processed:
  |
  +---> DuplicateAnalyzer.analyze(all_images) --> duplicate_groups
  +---> For each image: calculate quality_score
  +---> For each image: assign category (Good / Review / Poor)
  +---> Update DB with scores, categories, duplicate groups
       |
       v
[GET /api/photos] --> Frontend fetches results
       |
       v
User reviews --> [PATCH /api/photos/{id}/category] to reclassify
       |
       v
[POST /api/export] --> Copy selected files to export directory
```

---

## 6. Deployment Model

Single machine, local execution:

- Backend: `uvicorn` serving FastAPI on `localhost:8000`
- Frontend: Vite dev server on `localhost:5173` (development) or static build served by FastAPI (production)
- Database: SQLite file in `data/photosort.db`
- No external services, no cloud dependencies, no authentication required

---

## 7. Error Handling Strategy

| Layer | Strategy |
|-------|----------|
| Image Loading | Try/except around cv2.imread and PIL.Image.open; log and skip on failure |
| Individual Analyzer | Each analyzer wrapped in try/except; failed analysis recorded as error status |
| Pipeline | Individual image failure does not halt batch; error count tracked |
| API | FastAPI exception handlers return structured error responses |
| Frontend | API errors displayed as user-friendly messages |
| File System | Permission errors, missing files caught and reported |

---

## 8. Scalability Considerations (Future)

While not required for Version 1, the architecture supports:

- Replacing SQLite with PostgreSQL (SQLAlchemy ORM abstraction)
- Adding background task queues (FastAPI BackgroundTasks already used)
- Swapping MediaPipe face detection for a deep learning model
- Adding new analyzers by implementing the base analyzer interface
- Serving as a REST API for a mobile client
