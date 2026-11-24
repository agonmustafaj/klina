.PHONY: up db api frontend migrate pipeline-boundary pipeline-osm pipeline-import test

up:
	docker compose up -d db

db: up

migrate:
	cd backend && alembic upgrade head

api:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

pipeline-boundary:
	python pipeline/scripts/fetch_boundary.py

pipeline-osm:
	python pipeline/scripts/fetch_osm_clip.py

pipeline-import:
	python pipeline/scripts/import_postgis.py

test:
	cd backend && pytest -q
	cd frontend && npm run build
