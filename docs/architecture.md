# CityOS architecture

## Components

```
frontend/          Next.js App Router (dark GIS UI, MapLibre 2D, Cesium 3D gate)
backend/           FastAPI + SQLAlchemy/GeoAlchemy2
pipeline/          OSM acquisition, clip, PostGIS import
data/              boundary / raw / processed (payloads gitignored)
docker-compose.yml PostGIS 16 + API
```

## Data flow

1. `fetch_boundary.py` — Nominatim/OSM municipal polygon → `data/boundary/`
2. `fetch_osm_clip.py` — Geofabrik Kosovo PBF → clip to boundary → `data/processed/`
3. `import_postgis.py` — thematic GPKG → PostGIS + `data_coverage`
4. FastAPI GeoJSON/coverage endpoints
5. Frontend MapLibre / coverage-aware Cesium panel

## Integrity rules

- No fabricated geometries or statistics.
- Empty FeatureCollections and “Data unavailable” when layers are missing.
- `data_coverage.3d_buildings` drives the Cesium missing-coverage label.
