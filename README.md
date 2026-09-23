# PhotoSort

Automated Photo Quality Detection and Organization System

A BCA final-year project that processes collections of photographs, evaluates each image against multiple measurable quality parameters, assigns a numerical quality score, categorizes images into three tiers (Good / Review / Poor), and provides a review interface for manual adjustments and export.

## Features

- Blur detection using Laplacian variance
- Resolution analysis
- Exposure analysis using histogram-based brightness metrics
- Facial detection and closed-eye identification using MediaPipe
- Duplicate and near-duplicate detection using perceptual hashing
- Composite quality scoring with configurable weights
- Automatic categorization (Good / Review / Poor)
- Manual category reassignment
- Safe export (copy only, originals never modified)

## Tech Stack

- **Backend:** Python, FastAPI, OpenCV, MediaPipe, SQLAlchemy, SQLite
- **Frontend:** React, Vite, Vanilla CSS
- **Analysis:** OpenCV, NumPy, Pillow, imagehash

## Project Structure

```
photosort/
  backend/          # FastAPI application, analyzers, services
  frontend/         # React application
  docs/             # Project documentation
```

## Setup

See [docs/12-installation-guide.md](docs/12-installation-guide.md) for full instructions.

### Quick Start

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Documentation

| Document | Description |
|----------|-------------|
| [01-product-requirements.md](docs/01-product-requirements.md) | Functional and non-functional requirements |
| [02-system-architecture.md](docs/02-system-architecture.md) | Architecture, tech stack, data flow |
| [03-database-schema.md](docs/03-database-schema.md) | Database tables and relationships |
| [04-api-contracts.md](docs/04-api-contracts.md) | REST API endpoints and schemas |
| [05-analysis-pipeline.md](docs/05-analysis-pipeline.md) | Image analysis algorithms |
| [06-frontend-specification.md](docs/06-frontend-specification.md) | UI pages and design direction |
| [07-development-phases.md](docs/07-development-phases.md) | Implementation phases and estimates |
| [08-testing-strategy.md](docs/08-testing-strategy.md) | Test plan and methodology |
| [09-ui-design-system.md](docs/09-ui-design-system.md) | CSS design tokens and components |
| [10-scoring-engine.md](docs/10-scoring-engine.md) | Quality scoring formula and weights |
| [11-known-limitations.md](docs/11-known-limitations.md) | Honest limitations and mitigations |
| [12-installation-guide.md](docs/12-installation-guide.md) | Setup and troubleshooting |

## License

This project is developed as a BCA academic project.
