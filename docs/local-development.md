# Local development

## Prerequisites

- Docker + Docker Compose (PostGIS)
- Node.js 20+ and npm
- Python 3.12+

## Quick start

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Database + API
docker compose up -d db
cd backend && python -m venv .venv && source .venv/bin/activate
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
