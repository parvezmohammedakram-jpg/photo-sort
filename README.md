# PhotoSort

![PhotoSort Logo](frontend/public/icons.svg)

An **Automated Photo Quality Detection and Organization System**, built as a Bachelor of Computer Applications (BCA) project.

PhotoSort helps photographers and users automatically sort through large collections of photographs, scoring them on sharpness, exposure, and facial details, and categorizing them as Good, Review, or Poor. It also detects duplicate and near-duplicate photos to help reclaim storage space.

---

## ✨ Features

- **Automated Ingestion**: Safely ingest folders of images without modifying the originals.
- **Image Analysis Pipeline**:
  - **Blur Detection**: Calculates Laplacian variance to detect out-of-focus images.
  - **Exposure Analysis**: Uses histogram distributions to detect under and overexposed shots.
  - **Facial Analysis**: Detects faces and closed eyes using OpenCV Haar Cascades.
  - **Duplicate Detection**: Finds exact and near-duplicates using perceptual hashing (pHash) and exact hashing (MD5).
- **Quality Scoring**: A weighted scoring algorithm categorizes photos based on the analysis.
- **Dashboard & Results**: View comprehensive statistics, filter by category, and review duplicate groups.
- **Manual Review**: Override automated decisions if necessary.
- **Safe Export**: Copy categorized photos to a new destination folder without modifying the original source.

## 🏛️ Architecture & Documentation

For recruiters, professors, and contributors, the complete software engineering lifecycle documentation used to build this project is available in the [`docs/`](docs/) directory:

- [Product Requirements](docs/01-product-requirements.md)
- [System Architecture](docs/02-system-architecture.md)
- [Database Schema](docs/03-database-schema.md)
- [API Contracts](docs/04-api-contracts.md)
- [Analysis Pipeline Details](docs/05-analysis-pipeline.md)

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, OpenCV, ImageHash
- **Frontend**: React, Vite, React Router, Phosphor Icons, Axios, Vanilla CSS (Design engineered)

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher

### 1. Clone the Repository
```bash
git clone https://github.com/parvezmohammedakram-jpg/photo-sort.git
cd photo-sort
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
The backend API will be available at `http://127.0.0.1:8000`. API documentation is automatically generated at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the frontend development server
npm run dev
```
The frontend UI will be available at `http://localhost:5173`.

---

## 📖 Usage Guide

1. **Import**: Navigate to the Import view and specify a local directory containing your photos.
2. **Processing**: The system will automatically scan and begin analyzing the photos in the background. Wait for it to complete.
3. **Dashboard**: View aggregate statistics of your photo collection.
4. **Results**: Filter through Good, Review, and Poor photos. Click any photo to see detailed analysis metrics and manually override the category if needed.
5. **Duplicates**: Review groups of similar photos to help you cull redundant shots.
6. **Export**: Export specific categories (e.g., only "Good" photos) to a new destination folder. The original files remain untouched.

## 🎨 Design Philosophy

The user interface follows a "Neo Kinpaku" design system inspired by dark lacquer surfaces and gold leaf accents. The application is built with a focus on simplicity, responsiveness, and safe data handling (read-only source ingestion).
