# PhotoSort -- Installation Guide

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft (to be finalized after implementation)

---

## 1. Prerequisites

| Requirement | Minimum Version |
|------------|----------------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| Git | 2.30+ |
| Operating System | Windows 10/11, macOS 12+, or Ubuntu 20.04+ |

### Hardware

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| Processor | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| RAM | 8 GB | 16 GB |
| Storage | 256 GB SSD | 512 GB SSD |
| GPU | Not required | Dedicated GPU (faster MediaPipe inference) |

---

## 2. Installation Steps

### 2.1 Clone the Repository

```bash
git clone https://github.com/<username>/photosort.git
cd photosort
```

### 2.2 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

The backend should now be running at `http://localhost:8000`.

Verify: `http://localhost:8000/api/health` should return a JSON response.

### 2.3 Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend should now be running at `http://localhost:5173`.

---

## 3. Environment Configuration

The `.env` file contains configurable parameters. Copy `.env.example` and adjust as needed:

```bash
# Server
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/photosort.db

# Analysis thresholds
BLUR_SHARP_THRESHOLD=100.0
BLUR_BORDERLINE_THRESHOLD=50.0

MIN_WIDTH=1280
MIN_HEIGHT=720
MIN_MEGAPIXELS=1.0

EXPOSURE_LOW_BRIGHTNESS=60
EXPOSURE_HIGH_BRIGHTNESS=200

FACE_DETECTION_CONFIDENCE=0.5
EYE_CLOSED_THRESHOLD=0.18

DUPLICATE_HASH_THRESHOLD=10
DUPLICATE_HASH_SIZE=16

# Scoring
WEIGHT_SHARPNESS=0.35
WEIGHT_RESOLUTION=0.10
WEIGHT_EXPOSURE=0.30
WEIGHT_FACE=0.25

GOOD_THRESHOLD=70.0
REVIEW_THRESHOLD=40.0
DUPLICATE_PENALTY=10.0

# Processing
MAX_ANALYSIS_DIMENSION=2048
THUMBNAIL_SIZE=300
PREVIEW_SIZE=1200

# Supported formats
SUPPORTED_EXTENSIONS=.jpg,.jpeg,.png,.webp

# Logging
LOG_LEVEL=INFO
```

---

## 4. Running Tests

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate    # Windows
source venv/bin/activate  # macOS/Linux

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_blur.py -v
```

---

## 5. Quick Start (Demo Workflow)

1. Start the backend server (terminal 1)
2. Start the frontend server (terminal 2)
3. Open `http://localhost:5173` in a browser
4. Navigate to "Import"
5. Enter the path to a folder containing photographs
6. Click "Start Processing"
7. Watch the progress on the Processing page
8. Review results on the Results page
9. Click any photo for detailed analysis
10. Check the Duplicates page for duplicate groups
11. Change categories from the photo detail view
12. Export selected photos from the Export page

---

## 6. Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: cv2` | Ensure virtual environment is activated and `pip install opencv-python-headless` completed |
| `MediaPipe not found` | `pip install mediapipe` -- requires Python 3.10+ |
| Frontend cannot reach backend | Verify backend is running on port 8000; check CORS configuration |
| Database locked | Ensure only one instance of the backend is running |
| `Permission denied` on folder | Ensure the application has read access to the photo folder |
| Large images causing memory errors | Reduce MAX_ANALYSIS_DIMENSION in .env |
| Slow processing | Normal for large collections; consider processing in smaller batches |

---

## 7. Dependencies

### Backend (requirements.txt)

```
fastapi>=0.100.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
opencv-python-headless>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
mediapipe>=0.10.0
imagehash>=4.3.0
python-multipart>=0.0.6
aiofiles>=23.0.0
pydantic>=2.0.0
```

### Frontend (package.json dependencies)

```
react
react-dom
react-router-dom
axios (or fetch API)
```

Dev dependencies:

```
vite
@vitejs/plugin-react
```

---

## 8. Production Build (Optional)

For deployment or demonstration on a single machine:

```bash
# Build frontend
cd frontend
npm run build

# The build output in dist/ can be served by FastAPI as static files
```

This creates a self-contained setup where FastAPI serves both the API and the frontend.
