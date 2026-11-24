# Local development

## Prerequisites

- Docker + Docker Compose (PostGIS)
- Node.js 20+ and npm
- **Python 3.12 or 3.13** only (`backend/pyproject.toml`: `requires-python = ">=3.12,<3.14"`). Do not use 3.15.

## Quick start

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Database + API
docker compose up -d db
cd backend
# Windows:
#   py -3.12 -m venv .venv
#   .\.venv\Scripts\Activate.ps1
python3.12 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Or run API in Compose too: `docker compose up --build`.

## Geographic pipeline

See [data-sources.md](./data-sources.md). Boundary + OSM clip can run without PostGIS; import requires a healthy DB.

## Smoke checks

- http://localhost:8000/health
- http://localhost:8000/api/v1/coverage
- http://localhost:3000/
- http://localhost:3000/explore
