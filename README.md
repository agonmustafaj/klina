# CityOS — Digital Twin of Klina Municipality

Full-municipality digital twin for **Klina (Klinë), Kosovo**: Next.js + MapLibre/Cesium UI, FastAPI, PostGIS, OSM/Geofabrik pipeline.

**Hard rules:** real geographic data only; never fabricate buildings, roads, stats, or 3D city models; Cesium labels missing 3D coverage; no hardcoded frontend statistics.

## Repository layout

| Path | Role |
|------|------|
| `frontend/` | Next.js App Router (TypeScript, Tailwind, TanStack Query, Zustand, MapLibre) |
| `backend/` | FastAPI + Alembic + GeoAlchemy2 |
| `pipeline/` | Boundary fetch, Geofabrik clip, PostGIS import |
| `data/` | Boundary / raw / processed (binaries gitignored) |
| `docs/` | Architecture, data sources, local runbook |
| `docker-compose.yml` | PostGIS 16 (+ optional API) |

## Run locally

**Python:** **3.12 or 3.13 only** (`requires-python = ">=3.12,<3.14"` in `backend/pyproject.toml`).  
Do **not** use 3.15 — several deps (e.g. `psycopg-binary`) have no wheels yet.

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# PostGIS
docker compose up -d db

# API (Windows: py -3.12 -m venv .venv && .\.venv\Scripts\Activate.ps1)
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — Explore map at `/explore`.

### Load real OSM data

```bash
pip install -r pipeline/requirements.txt
python pipeline/scripts/fetch_boundary.py
python pipeline/scripts/fetch_osm_clip.py   # downloads Geofabrik Kosovo PBF; may take several minutes
DATABASE_URL=postgresql+psycopg://cityos:cityos@localhost:5432/cityos \
  python pipeline/scripts/import_postgis.py
```

## Cloudflare Pages

Frontend is a **static export** (`output: "export"` → `frontend/out`).

| Field | Value |
|-------|--------|
| Root directory | `frontend` |
| Build command | `npm run build` |
| Build output directory | `out` |
| Framework preset | Next.js (or None) |

Set `NEXT_PUBLIC_API_URL` to your public FastAPI origin when the API is hosted. Until then the UI falls back to `http://localhost:8000` (works only on your machine).

## Docs

- [Architecture](docs/architecture.md)
- [Data sources](docs/data-sources.md)
- [Local development](docs/local-development.md)
