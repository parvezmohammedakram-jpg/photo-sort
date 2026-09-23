# PhotoSort -- Database Schema Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Overview

PhotoSort uses SQLite as its database engine, accessed through SQLAlchemy ORM. The schema stores image metadata, analysis results, manual review state, duplicate group assignments, and project sessions. Image binary data is never stored in the database.

---

## 2. Entity Relationship Diagram

```
+---------------+       1:1       +------------------+       1:1       +------------------+
|               |---------------->|                  |---------------->|                  |
|    Project    |  1:N            |      Photo       |                 |  ManualReview    |
|               |<----------------|                  |<----------------|                  |
+---------------+                 +------------------+                 +------------------+
                                         |
                                         | 1:1
                                         v
                                  +------------------+
                                  |                  |
                                  |    Analysis      |
                                  |                  |
                                  +------------------+

+------------------+       M:N (via photo.duplicate_group_id)
|                  |
| DuplicateGroup   |<---- Photo.duplicate_group_id (nullable FK)
|                  |
+------------------+
```

---

## 3. Table Definitions

### 3.1 projects

Represents a processing session (one folder import).

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique project identifier |
| name | VARCHAR(255) | NOT NULL | User-provided or auto-generated project name |
| source_path | TEXT | NOT NULL | Absolute path to the source folder |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending, processing, completed, failed |
| total_files | INTEGER | DEFAULT 0 | Total files discovered in folder |
| supported_files | INTEGER | DEFAULT 0 | Files with supported extensions |
| processed_files | INTEGER | DEFAULT 0 | Files successfully processed |
| failed_files | INTEGER | DEFAULT 0 | Files that failed processing |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Project creation time |
| completed_at | DATETIME | NULLABLE | Processing completion time |

### 3.2 photos

Stores metadata for each discovered image file.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique photo identifier |
| project_id | INTEGER | NOT NULL, FK(projects.id) | Parent project |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| filepath | TEXT | NOT NULL | Absolute path to original file |
| file_size | INTEGER | NOT NULL | File size in bytes |
| width | INTEGER | NULLABLE | Image width in pixels |
| height | INTEGER | NULLABLE | Image height in pixels |
| megapixels | REAL | NULLABLE | Width * Height / 1,000,000 |
| format | VARCHAR(10) | NOT NULL | File extension (jpg, png, webp) |
| thumbnail_path | TEXT | NULLABLE | Path to generated thumbnail |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending, processing, completed, failed |
| error_message | TEXT | NULLABLE | Error details if processing failed |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:**
- `idx_photos_project_id` on `project_id`
- `idx_photos_status` on `status`

### 3.3 analyses

Stores all analysis results for a successfully processed photo. One-to-one with photos.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique analysis identifier |
| photo_id | INTEGER | NOT NULL, UNIQUE, FK(photos.id) | Associated photo |
| sharpness_score | REAL | NULLABLE | Laplacian variance value |
| blur_status | VARCHAR(20) | NULLABLE | sharp, borderline, blurry |
| brightness_avg | REAL | NULLABLE | Average brightness (0-255) |
| dark_pixel_pct | REAL | NULLABLE | Percentage of dark pixels |
| bright_pixel_pct | REAL | NULLABLE | Percentage of bright pixels |
| exposure_status | VARCHAR(20) | NULLABLE | underexposed, good, overexposed |
| face_count | INTEGER | DEFAULT 0 | Number of detected faces |
| closed_eye_detected | BOOLEAN | DEFAULT FALSE | Whether closed eyes were detected |
| face_status | VARCHAR(30) | NULLABLE | no_face, faces_detected, closed_eyes, analysis_failed |
| duplicate_group_id | INTEGER | NULLABLE, FK(duplicate_groups.id) | Duplicate group assignment |
| duplicate_hash | VARCHAR(64) | NULLABLE | Perceptual hash for comparison |
| file_hash | VARCHAR(64) | NULLABLE | MD5/SHA hash for exact match |
| quality_score | REAL | NULLABLE | Overall quality score (0-100) |
| category | VARCHAR(20) | DEFAULT 'pending' | good, review, poor, pending |
| processed_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Analysis completion time |

**Indexes:**
- `idx_analyses_photo_id` on `photo_id`
- `idx_analyses_category` on `category`
- `idx_analyses_quality_score` on `quality_score`
- `idx_analyses_duplicate_group` on `duplicate_group_id`
- `idx_analyses_file_hash` on `file_hash`

### 3.4 duplicate_groups

Represents a group of images identified as duplicates or near-duplicates.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique group identifier |
| project_id | INTEGER | NOT NULL, FK(projects.id) | Parent project |
| group_type | VARCHAR(20) | NOT NULL | exact, near_duplicate |
| similarity_score | REAL | NULLABLE | Average similarity within group (0-100) |
| member_count | INTEGER | DEFAULT 0 | Number of photos in this group |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Group creation time |

### 3.5 manual_reviews

Tracks manual category changes made by the user.

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique review identifier |
| photo_id | INTEGER | NOT NULL, FK(photos.id) | Associated photo |
| original_category | VARCHAR(20) | NOT NULL | Category before manual change |
| new_category | VARCHAR(20) | NOT NULL | Category after manual change |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Time of manual change |

**Index:**
- `idx_manual_reviews_photo_id` on `photo_id`

---

## 4. Relationship Summary

| Relationship | Type | Description |
|-------------|------|-------------|
| Project -> Photos | One-to-Many | A project contains many photos |
| Photo -> Analysis | One-to-One | Each photo has exactly one analysis record |
| Photo -> ManualReviews | One-to-Many | A photo may have multiple review history entries |
| DuplicateGroup -> Photos (via Analysis) | One-to-Many | A group contains multiple photos |
| Project -> DuplicateGroups | One-to-Many | Groups belong to a project |

---

## 5. Category Values

| Value | Meaning |
|-------|---------|
| good | Image meets quality thresholds |
| review | Borderline quality, needs human judgment |
| poor | Significant quality problems detected |
| pending | Not yet scored/classified |

---

## 6. Status Values

### Project Status

| Value | Meaning |
|-------|---------|
| pending | Created but processing not started |
| processing | Currently processing images |
| completed | All images processed |
| failed | Processing encountered a fatal error |

### Photo Status

| Value | Meaning |
|-------|---------|
| pending | Discovered but not yet analyzed |
| processing | Currently being analyzed |
| completed | Analysis finished successfully |
| failed | Analysis failed (error_message contains details) |

---

## 7. Design Decisions

1. **Separate analysis table**: Keeps the photo table lightweight. Analysis can be rerun without losing photo metadata.

2. **Manual review as a log**: Multiple entries per photo allow tracking the full history of category changes, not just the current state. The current category lives in the analysis table for query efficiency.

3. **Duplicate groups as a separate table**: Cleaner than storing group membership as JSON arrays. Allows efficient queries like "show all groups" and "show all members of group X."

4. **No image storage**: Only file paths are stored. This keeps the database small and avoids unnecessary data duplication.

5. **Nullable analysis fields**: If an individual analyzer fails, the remaining fields can still be populated. A photo with a failed face analysis can still have valid blur and exposure results.
