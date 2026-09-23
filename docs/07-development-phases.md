# PhotoSort -- Development Phases Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## Phase 0: Requirements and Architecture (Current)

**Objective:** Understand, plan, and document before writing code.

**Deliverables:**
- [x] Product requirements document
- [x] System architecture document
- [x] Database schema document
- [x] API contracts document
- [x] Analysis pipeline document
- [x] Frontend specification document
- [x] Development phases document
- [x] Testing strategy document
- [x] UI design system document
- [x] Scoring engine specification
- [x] Known limitations document
- [ ] Review and approval from stakeholder

**Exit Criteria:** All documents reviewed, questions resolved, approval to proceed.

---

## Phase 1: Project Foundation

**Objective:** Set up the project skeleton so both backend and frontend can run.

**Backend Tasks:**
- Initialize Python project with virtual environment
- Install core dependencies (FastAPI, uvicorn, SQLAlchemy, OpenCV, Pillow, NumPy)
- Create directory structure
- Implement centralized configuration (config.py with all thresholds)
- Set up logging (logger.py)
- Initialize SQLite database with SQLAlchemy models
- Create FastAPI application entry point
- Implement health check endpoint (`GET /api/health`)
- Create `.env.example` with default configuration
- Create `requirements.txt`

**Frontend Tasks:**
- Initialize React project with Vite
- Set up CSS design system (variables, base styles)
- Create Layout component (sidebar + main area)
- Create placeholder pages (Dashboard, Import, Results, etc.)
- Set up API client service
- Verify frontend can reach backend health endpoint

**Verification:**
- `uvicorn app.main:app --reload` starts without errors
- `npm run dev` starts without errors
- Health endpoint returns 200
- Frontend renders the shell layout

**Estimated Effort:** 1-2 days

---

## Phase 2: Image Ingestion

**Objective:** Accept a folder path, discover images, validate them, and store metadata.

**Tasks:**
- Implement file discovery service (scan folder, filter extensions)
- Implement file validation (check integrity with PIL/cv2)
- Implement metadata extraction (dimensions, file size, format)
- Create Project model and API endpoints (POST /api/projects, GET /api/projects)
- Store photo records in database
- Handle unsupported files, corrupted images, permission errors
- Build Import view in frontend (folder path input, project name, start button)
- Display file counts after discovery

**Verification:**
- Point at a folder with mixed files (images + non-images)
- Verify correct file counts
- Verify corrupted images are logged and skipped
- Verify photo records appear in database

**Estimated Effort:** 2-3 days

---

## Phase 3: Image Analysis Engine

**Objective:** Implement all five analyzers as independent, testable modules.

**Sub-phases:**

### Phase 3a: Blur Analyzer
- Implement Laplacian variance calculation
- Implement threshold classification
- Write unit tests (sharp, borderline, blurry images)
- Calibrate thresholds against sample images

### Phase 3b: Resolution Analyzer
- Implement dimension and megapixel calculation
- Implement threshold comparison
- Write unit tests (high-res, low-res)

### Phase 3c: Exposure Analyzer
- Implement histogram-based brightness analysis
- Implement dark/bright pixel percentage calculation
- Implement multi-indicator classification
- Write unit tests (underexposed, normal, overexposed)

### Phase 3d: Face Analyzer
- Set up MediaPipe Face Detection and Face Mesh
- Implement face detection with confidence threshold
- Implement Eye Aspect Ratio calculation
- Implement closed-eye detection
- Write unit tests (no face, one face, multiple faces)
- Document limitations

### Phase 3e: Duplicate Analyzer
- Implement MD5 file hashing for exact duplicates
- Implement perceptual hashing using imagehash library
- Implement Hamming distance comparison
- Implement group formation
- Write unit tests (exact duplicate, resized copy, similar image, unrelated image)

**Verification:**
- Each analyzer passes its unit tests independently
- Analyzers produce sensible results on real sample images
- Threshold values documented and justified

**Estimated Effort:** 4-5 days

---

## Phase 4: Quality Scoring

**Objective:** Combine analysis results into a single quality score and category.

**Tasks:**
- Implement score normalization for each metric
- Implement weighted scoring model
- Implement duplicate penalty
- Implement category classification (Good / Review / Poor)
- Write unit tests for scoring edge cases
- Document scoring formula, weights, and thresholds

**Verification:**
- Known-good analysis inputs produce expected score ranges
- Category boundaries work correctly at threshold values
- Scoring is deterministic (same input = same output)

**Estimated Effort:** 1-2 days

---

## Phase 5: Processing Pipeline

**Objective:** Connect all components into an end-to-end processing flow.

**Tasks:**
- Implement pipeline orchestrator (services/pipeline.py)
- Implement per-image error isolation
- Implement thumbnail generation
- Implement processing status tracking
- Create processing API endpoints (POST /process, GET /status)
- Implement background task execution
- Integrate duplicate analysis as a post-processing step
- Integrate scoring and classification after all images processed

**Verification:**
- Process a folder of 20+ images end-to-end
- Verify corrupted images are skipped without stopping batch
- Verify all results stored in database
- Verify thumbnails generated
- Verify processing status updates correctly

**Estimated Effort:** 2-3 days

---

## Phase 6: Frontend

**Objective:** Build all UI views connected to real API data.

**Tasks:**
- Dashboard view with live statistics from API
- Processing view with real progress polling
- Results grid view with category filtering and pagination
- Photo detail view with full analysis display
- Duplicate groups view
- Export view
- Thumbnail rendering from API
- Error state handling

**Verification:**
- Complete workflow: Import -> Process -> View Results -> View Detail -> View Duplicates
- All data displayed matches database records
- Category filters work correctly
- Pagination works correctly

**Estimated Effort:** 4-5 days

---

## Phase 7: Manual Review

**Objective:** Allow users to change photo categories.

**Tasks:**
- Implement PATCH /api/photos/{id}/category endpoint
- Implement manual_reviews table logging
- Add category change buttons in photo detail view
- Update UI optimistically on category change
- Refresh dashboard counts after changes
- Track manually modified status

**Verification:**
- Change a photo from Review to Good
- Verify database updated
- Verify manual_reviews record created
- Verify dashboard count updated
- Verify is_manually_modified flag set

**Estimated Effort:** 1 day

---

## Phase 8: Export

**Objective:** Allow users to copy selected photos to an output directory.

**Tasks:**
- Implement export service (safe file copying)
- Implement POST /api/export endpoint
- Build export view in frontend
- Support export by category and by selection
- Implement export progress reporting
- Verify originals remain untouched

**Verification:**
- Export Good photos to a new directory
- Verify files copied correctly
- Verify originals unchanged (file hash comparison)
- Verify missing source files handled gracefully

**Estimated Effort:** 1-2 days

---

## Phase 9: Testing and Hardening

**Objective:** Comprehensive testing and bug fixing.

**Tasks:**
- Run full unit test suite
- Write API integration tests
- Test with large batch (100+ images)
- Test with all-corrupted folder
- Test with empty folder
- Test with single image
- Test with very large images (50+ MP)
- Fix discovered bugs
- Performance profiling (identify bottlenecks)
- Memory usage monitoring

**Verification:**
- All tests pass
- No crashes on edge cases
- Processing completes within reasonable time for 100+ images
- Memory usage stays bounded

**Estimated Effort:** 2-3 days

---

## Phase 10: Documentation

**Objective:** Produce final documentation for project submission.

**Tasks:**
- Final README.md with setup instructions
- Installation guide (step-by-step from clean environment)
- Architecture documentation (finalized)
- API documentation (finalized or auto-generated from OpenAPI)
- Database documentation (finalized)
- User guide (how to use the application)
- Testing documentation (methodology, results, accuracy evaluation)
- Known limitations document (finalized)
- Future scope document

**Verification:**
- A fresh environment can install and run the application following only the README
- All documents are consistent with the implemented application

**Estimated Effort:** 2 days

---

## Total Estimated Effort

| Phase | Days |
|-------|------|
| Phase 0: Requirements and Architecture | 1-2 |
| Phase 1: Project Foundation | 1-2 |
| Phase 2: Image Ingestion | 2-3 |
| Phase 3: Analysis Engine | 4-5 |
| Phase 4: Quality Scoring | 1-2 |
| Phase 5: Processing Pipeline | 2-3 |
| Phase 6: Frontend | 4-5 |
| Phase 7: Manual Review | 1 |
| Phase 8: Export | 1-2 |
| Phase 9: Testing and Hardening | 2-3 |
| Phase 10: Documentation | 2 |
| **Total** | **21-30 days** |

This estimate assumes focused development. Buffer 20-30% for unexpected issues.
