# PhotoSort -- API Contracts Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Overview

All endpoints are served under the `/api` prefix. The backend runs on `http://localhost:8000`. Responses use JSON. Error responses follow a consistent structure.

---

## 2. Common Response Envelope

### Success Response

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response

```json
{
  "status": "error",
  "detail": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

### Pagination (where applicable)

```json
{
  "status": "success",
  "data": [ ... ],
  "pagination": {
    "total": 1248,
    "page": 1,
    "per_page": 50,
    "total_pages": 25
  }
}
```

---

## 3. Endpoints

---

### 3.1 Health Check

**GET** `/api/health`

Returns application health status. No authentication required.

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "service": "photosort",
    "version": "1.0.0",
    "database": "connected"
  }
}
```

---

### 3.2 Projects

#### Create Project

**POST** `/api/projects`

Creates a new processing project from a folder path.

**Request Body:**

```json
{
  "name": "Wedding Photos 2024",
  "source_path": "C:/Users/parve/Photos/Wedding"
}
```

**Response 201:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Wedding Photos 2024",
    "source_path": "C:/Users/parve/Photos/Wedding",
    "status": "pending",
    "total_files": 0,
    "supported_files": 0,
    "processed_files": 0,
    "failed_files": 0,
    "created_at": "2026-09-23T12:00:00"
  }
}
```

**Error Cases:**

| Code | Condition |
|------|-----------|
| 400 | Invalid or empty source path |
| 404 | Source path does not exist |
| 400 | Source path is not a directory |

---

#### Get Project

**GET** `/api/projects/{project_id}`

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Wedding Photos 2024",
    "source_path": "C:/Users/parve/Photos/Wedding",
    "status": "completed",
    "total_files": 1500,
    "supported_files": 1248,
    "processed_files": 1240,
    "failed_files": 8,
    "created_at": "2026-09-23T12:00:00",
    "completed_at": "2026-09-23T12:15:30"
  }
}
```

---

#### List Projects

**GET** `/api/projects`

**Response 200:**

```json
{
  "status": "success",
  "data": [
    { "id": 1, "name": "Wedding Photos 2024", "status": "completed", "supported_files": 1248, "created_at": "..." },
    { "id": 2, "name": "Trip Photos", "status": "processing", "supported_files": 342, "created_at": "..." }
  ]
}
```

---

### 3.3 Processing

#### Start Processing

**POST** `/api/projects/{project_id}/process`

Initiates the analysis pipeline for a project. Runs as a background task.

**Response 202:**

```json
{
  "status": "success",
  "data": {
    "message": "Processing started",
    "project_id": 1
  }
}
```

**Error Cases:**

| Code | Condition |
|------|-----------|
| 404 | Project not found |
| 409 | Project already processing or completed |

---

#### Get Processing Status

**GET** `/api/projects/{project_id}/status`

Returns real-time processing progress.

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "project_id": 1,
    "project_status": "processing",
    "total": 1248,
    "processed": 897,
    "failed": 3,
    "progress_percent": 71.9,
    "current_file": "IMG_0897.jpg",
    "current_step": "exposure_analysis"
  }
}
```

---

### 3.4 Photos

#### List Photos

**GET** `/api/projects/{project_id}/photos`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| category | string | all | Filter: good, review, poor, all |
| page | integer | 1 | Page number |
| per_page | integer | 50 | Items per page (max 100) |
| sort_by | string | quality_score | Sort field: quality_score, filename, created_at |
| sort_order | string | desc | asc or desc |

**Response 200:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 42,
      "filename": "IMG_1048.jpg",
      "thumbnail_url": "/api/photos/42/thumbnail",
      "quality_score": 91.2,
      "category": "good",
      "blur_status": "sharp",
      "exposure_status": "good",
      "face_count": 2,
      "is_duplicate": false,
      "is_manually_modified": false
    }
  ],
  "pagination": {
    "total": 742,
    "page": 1,
    "per_page": 50,
    "total_pages": 15
  }
}
```

---

#### Get Photo Detail

**GET** `/api/photos/{photo_id}`

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "id": 42,
    "filename": "IMG_1048.jpg",
    "filepath": "C:/Users/parve/Photos/Wedding/IMG_1048.jpg",
    "file_size": 4523000,
    "width": 4032,
    "height": 3024,
    "megapixels": 12.19,
    "format": "jpg",
    "thumbnail_url": "/api/photos/42/thumbnail",
    "preview_url": "/api/photos/42/preview",
    "status": "completed",
    "analysis": {
      "sharpness_score": 824.2,
      "blur_status": "sharp",
      "brightness_avg": 126.7,
      "dark_pixel_pct": 6.3,
      "bright_pixel_pct": 3.8,
      "exposure_status": "good",
      "face_count": 3,
      "closed_eye_detected": false,
      "face_status": "faces_detected",
      "quality_score": 87.4,
      "category": "good",
      "duplicate_group_id": null,
      "is_manually_modified": false,
      "processed_at": "2026-09-23T12:05:42"
    },
    "detected_issues": [],
    "created_at": "2026-09-23T12:00:05"
  }
}
```

When issues exist:

```json
"detected_issues": [
  "Possible closed eyes detected",
  "Image is slightly underexposed"
]
```

---

#### Get Photo Thumbnail

**GET** `/api/photos/{photo_id}/thumbnail`

Returns the thumbnail image file (JPEG, 300px max dimension).

**Response 200:** Binary image data with `Content-Type: image/jpeg`

---

#### Get Photo Preview

**GET** `/api/photos/{photo_id}/preview`

Returns a larger preview image (1200px max dimension).

**Response 200:** Binary image data with `Content-Type: image/jpeg`

---

#### Update Photo Category

**PATCH** `/api/photos/{photo_id}/category`

Manually reassign a photo's category.

**Request Body:**

```json
{
  "category": "good"
}
```

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "id": 42,
    "previous_category": "review",
    "new_category": "good",
    "is_manually_modified": true
  }
}
```

**Error Cases:**

| Code | Condition |
|------|-----------|
| 404 | Photo not found |
| 400 | Invalid category value |

---

### 3.5 Statistics

**GET** `/api/projects/{project_id}/statistics`

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "total_photos": 1248,
    "processed": 1240,
    "failed": 8,
    "categories": {
      "good": 742,
      "review": 301,
      "poor": 197
    },
    "duplicate_groups": 34,
    "duplicate_photos": 86,
    "average_quality_score": 68.4,
    "issues": {
      "blurry": 89,
      "underexposed": 42,
      "overexposed": 18,
      "low_resolution": 31,
      "closed_eyes": 15
    }
  }
}
```

---

### 3.6 Duplicates

**GET** `/api/projects/{project_id}/duplicates`

**Response 200:**

```json
{
  "status": "success",
  "data": [
    {
      "group_id": 1,
      "group_type": "near_duplicate",
      "similarity_score": 96.2,
      "member_count": 3,
      "photos": [
        {
          "id": 45,
          "filename": "IMG_1045.jpg",
          "thumbnail_url": "/api/photos/45/thumbnail",
          "quality_score": 82.1
        },
        {
          "id": 46,
          "filename": "IMG_1046.jpg",
          "thumbnail_url": "/api/photos/46/thumbnail",
          "quality_score": 79.3
        },
        {
          "id": 47,
          "filename": "IMG_1047.jpg",
          "thumbnail_url": "/api/photos/47/thumbnail",
          "quality_score": 85.7
        }
      ]
    }
  ]
}
```

---

### 3.7 Export

**POST** `/api/projects/{project_id}/export`

Copies selected photos to an output directory.

**Request Body:**

```json
{
  "export_type": "by_category",
  "categories": ["good"],
  "output_path": "C:/Users/parve/PhotoSort_Export"
}
```

Alternative (export specific photo IDs):

```json
{
  "export_type": "selected",
  "photo_ids": [42, 45, 67, 89],
  "output_path": "C:/Users/parve/PhotoSort_Export"
}
```

**Response 200:**

```json
{
  "status": "success",
  "data": {
    "exported_count": 742,
    "output_path": "C:/Users/parve/PhotoSort_Export",
    "structure": {
      "Good": 742
    }
  }
}
```

**Error Cases:**

| Code | Condition |
|------|-----------|
| 404 | Project not found |
| 400 | Invalid output path |
| 400 | No photos match criteria |

---

## 4. Error Code Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Request body fails validation |
| NOT_FOUND | 404 | Resource does not exist |
| CONFLICT | 409 | Operation conflicts with current state |
| PATH_INVALID | 400 | File system path is invalid or unsafe |
| PATH_NOT_FOUND | 404 | File system path does not exist |
| PROCESSING_FAILED | 500 | Processing pipeline encountered a fatal error |
| EXPORT_FAILED | 500 | Export operation failed |
