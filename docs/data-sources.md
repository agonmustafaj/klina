# Data sources

| Dataset | Source | License / terms | Status |
|---------|--------|-----------------|--------|
| Municipal boundary | OpenStreetMap via Nominatim | ODbL | Pipeline: `fetch_boundary.py` |
| Roads, buildings, places, POI, landuse, water | Geofabrik Kosovo extract (`europe/kosovo-latest.osm.pbf`) clipped to boundary | ODbL | Pipeline: `fetch_osm_clip.py` |
| Demographics | — | — | Not acquired — UI shows Data unavailable |
| 3D city model / LOD2 | — | — | Not acquired — Cesium labels missing coverage |
| Official cadastre / planning | — | — | Inventory pending; only open licensed data will be used |

## Acquisition commands

```bash
pip install -r pipeline/requirements.txt
python pipeline/scripts/fetch_boundary.py
python pipeline/scripts/fetch_osm_clip.py
# requires PostGIS + alembic upgrade head
python pipeline/scripts/import_postgis.py
```

Provenance for each run is written to `data/boundary/klina_boundary.meta.json` and `data/processed/acquisition_manifest.json` (local only; large binaries gitignored).
