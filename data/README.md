# CityOS data directory

| Path | Purpose |
|------|---------|
| `boundary/` | Verified municipal boundary GeoJSON + provenance meta |
| `raw/` | Upstream downloads (e.g. Geofabrik Kosovo `.osm.pbf`) — gitignored |
| `processed/` | Clipped / thematic layers — gitignored |

**Hard rule:** never place fabricated geometries or statistics here. All files must trace to an open source recorded in `docs/data-sources.md`.

## Acquisition

```bash
# from repo root
python -m venv .venv && source .venv/bin/activate
pip install -r pipeline/requirements.txt
python pipeline/scripts/fetch_boundary.py
python pipeline/scripts/fetch_osm_clip.py
# after PostGIS is up + migrations applied:
python pipeline/scripts/import_postgis.py
```
