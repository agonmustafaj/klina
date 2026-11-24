#!/usr/bin/env python3
"""Import processed GeoPackage layers into PostGIS and update data_coverage.

Usage:
  DATABASE_URL=postgresql+psycopg://cityos:cityos@localhost:5432/cityos \\
    python pipeline/scripts/import_postgis.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import geopandas as gpd
from geoalchemy2 import Geometry
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
BOUNDARY_GEOJSON = ROOT / "data" / "boundary" / "klina_boundary.geojson"
META_PATH = ROOT / "data" / "boundary" / "klina_boundary.meta.json"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://cityos:cityos@localhost:5432/cityos",
)


def upsert_coverage(conn, layer: str, status: str, count: int, source: str, notes: str, has_3d: bool = False):
    conn.execute(
        text(
            """
            INSERT INTO data_coverage (layer, status, feature_count, has_3d, source, notes, updated_at)
            VALUES (:layer, :status, :count, :has_3d, :source, :notes, NOW())
            ON CONFLICT (layer) DO UPDATE SET
              status = EXCLUDED.status,
              feature_count = EXCLUDED.feature_count,
              has_3d = EXCLUDED.has_3d,
              source = EXCLUDED.source,
              notes = EXCLUDED.notes,
              updated_at = NOW()
            """
        ),
        {
            "layer": layer,
            "status": status,
            "count": count,
            "has_3d": has_3d,
            "source": source,
            "notes": notes,
        },
    )


def import_boundary(engine) -> int:
    if not BOUNDARY_GEOJSON.exists():
        print("Boundary GeoJSON missing — skip")
        return 0
    gdf = gpd.read_file(BOUNDARY_GEOJSON).to_crs(4326)
    meta = {}
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM municipal_boundary"))
        for _, row in gdf.iterrows():
            geom_wkt = row.geometry.wkt
            # Force multipolygon
            if row.geometry.geom_type == "Polygon":
                from shapely.geometry import MultiPolygon

                geom_wkt = MultiPolygon([row.geometry]).wkt
            props = row.get("properties") if False else {}  # noqa: keep simple
            name = row.get("name") or "Klina"
            name_local = row.get("name_local") or "Klinë"
            osm_id = row.get("osm_id") or meta.get("osm_id")
            area = row.get("area_km2_computed")
            conn.execute(
                text(
                    """
                    INSERT INTO municipal_boundary
                      (name, name_local, osm_relation_id, source, source_url, area_km2, geom)
                    VALUES
                      (:name, :name_local, :osm_id, :source, :source_url, :area,
                       ST_SetSRID(ST_GeomFromText(:geom), 4326))
                    """
                ),
                {
                    "name": name,
                    "name_local": name_local,
                    "osm_id": int(osm_id) if osm_id else None,
                    "source": "OpenStreetMap via Nominatim",
                    "source_url": meta.get("source_url") or "https://www.openstreetmap.org/",
                    "area": float(area) if area is not None else None,
                    "geom": geom_wkt,
                },
            )
        upsert_coverage(
            conn,
            "municipal_boundary",
            "present",
            len(gdf),
            "OpenStreetMap via Nominatim",
            "Verified municipal admin boundary",
        )
    return len(gdf)


def import_gpkg(engine, path: Path, table: str, mapper) -> int:
    if not path.exists():
        print(f"Missing {path} — marking {table} unavailable")
        with engine.begin() as conn:
            upsert_coverage(conn, table, "missing", 0, "OSM/Geofabrik", "Data unavailable")
        return 0
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    else:
        gdf = gdf.to_crs(4326)
    count = mapper(engine, gdf)
    return count


def map_settlements(engine, gdf) -> int:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM settlements"))
        n = 0
        for _, row in gdf.iterrows():
            if row.geometry is None or row.geometry.is_empty:
                continue
            geom = row.geometry
            if geom.geom_type != "Point":
                geom = geom.representative_point()
            name = row.get("name") or row.get("name:en")
            if not name or (isinstance(name, float)):
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO settlements (osm_id, name, name_local, place_type, population, source, geom)
                    VALUES (:osm_id, :name, :name_local, :place, :pop, :source,
                            ST_SetSRID(ST_GeomFromText(:geom), 4326))
                    """
                ),
                {
                    "osm_id": int(row["osm_id"]) if "osm_id" in row and row.get("osm_id") == row.get("osm_id") else None,
                    "name": str(name),
                    "name_local": str(row["name:sq"]) if row.get("name:sq") == row.get("name:sq") and row.get("name:sq") else None,
                    "place": str(row["place"]) if row.get("place") == row.get("place") else None,
                    "pop": int(row["population"]) if row.get("population") == row.get("population") and str(row.get("population")).isdigit() else None,
                    "source": "OSM/Geofabrik Kosovo clipped to Klina",
                    "geom": geom.wkt,
                },
            )
            n += 1
        upsert_coverage(
            conn,
            "settlements",
            "present" if n else "missing",
            n,
            "OSM/Geofabrik",
            "Place nodes from OSM clip" if n else "Data unavailable",
        )
    return n


def map_buildings(engine, gdf) -> int:
    from shapely.geometry import MultiPolygon, Polygon

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM buildings"))
        n = 0
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue
            if geom.geom_type == "Polygon":
                geom = MultiPolygon([geom])
            elif geom.geom_type != "MultiPolygon":
                continue
            levels = None
            if row.get("building:levels") == row.get("building:levels"):
                try:
                    levels = int(float(row.get("building:levels")))
                except (TypeError, ValueError):
                    levels = None
            height = None
            if row.get("height") == row.get("height"):
                try:
                    height = float(str(row.get("height")).replace("m", "").strip())
                except (TypeError, ValueError):
                    height = None
            # has_3d only when real height/levels exist — never fake 3D
            has_3d = bool(height) or bool(levels)
            conn.execute(
                text(
                    """
                    INSERT INTO buildings
                      (osm_id, building_type, name, levels, height_m, has_3d, source, geom)
                    VALUES
                      (:osm_id, :btype, :name, :levels, :height, :has_3d, :source,
                       ST_SetSRID(ST_GeomFromText(:geom), 4326))
                    """
                ),
                {
                    "osm_id": int(row["osm_id"]) if "osm_id" in gdf.columns and row.get("osm_id") == row.get("osm_id") else None,
                    "btype": str(row["building"]) if row.get("building") == row.get("building") else None,
                    "name": str(row["name"]) if row.get("name") == row.get("name") and row.get("name") else None,
                    "levels": levels,
                    "height": height,
                    "has_3d": has_3d,
                    "source": "OSM/Geofabrik Kosovo clipped to Klina",
                    "geom": geom.wkt,
                },
            )
            n += 1
        upsert_coverage(
            conn,
            "buildings",
            "present" if n else "missing",
            n,
            "OSM/Geofabrik",
            "Building footprints from OSM" if n else "Data unavailable",
        )
        # 3D coverage is partial at best from OSM tags — never claim full 3D city
        with_3d = conn.execute(text("SELECT COUNT(*) FROM buildings WHERE has_3d = true")).scalar() or 0
        upsert_coverage(
            conn,
            "3d_buildings",
            "partial" if with_3d else "missing",
            int(with_3d),
            "OSM tags (height/building:levels) only",
            "No photogrammetry/LOD2 city model. Cesium must label missing 3D coverage.",
            has_3d=bool(with_3d),
        )
    return n


def map_roads(engine, gdf) -> int:
    from shapely.geometry import LineString, MultiLineString

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM roads"))
        n = 0
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue
            if geom.geom_type == "LineString":
                geom = MultiLineString([geom])
            elif geom.geom_type != "MultiLineString":
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO roads (osm_id, name, highway, surface, source, geom)
                    VALUES (:osm_id, :name, :highway, :surface, :source,
                            ST_SetSRID(ST_GeomFromText(:geom), 4326))
                    """
                ),
                {
                    "osm_id": int(row["osm_id"]) if "osm_id" in gdf.columns and row.get("osm_id") == row.get("osm_id") else None,
                    "name": str(row["name"]) if row.get("name") == row.get("name") and row.get("name") else None,
                    "highway": str(row["highway"]) if row.get("highway") == row.get("highway") else None,
                    "surface": str(row["surface"]) if row.get("surface") == row.get("surface") and row.get("surface") else None,
                    "source": "OSM/Geofabrik Kosovo clipped to Klina",
                    "geom": geom.wkt,
                },
            )
            n += 1
        upsert_coverage(
            conn,
            "roads",
            "present" if n else "missing",
            n,
            "OSM/Geofabrik",
            "Highway network from OSM" if n else "Data unavailable",
        )
    return n


def map_poi(engine, gdf) -> int:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM points_of_interest"))
        n = 0
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom is None or geom.is_empty:
                continue
            if geom.geom_type != "Point":
                geom = geom.representative_point()
            category = None
            subcategory = None
            for key in ("amenity", "shop", "tourism", "healthcare", "office"):
                if key in gdf.columns and row.get(key) == row.get(key) and row.get(key):
                    category = key
                    subcategory = str(row.get(key))
                    break
            name = row.get("name") if row.get("name") == row.get("name") else None
            conn.execute(
                text(
                    """
                    INSERT INTO points_of_interest
                      (osm_id, name, category, subcategory, source, geom)
                    VALUES (:osm_id, :name, :cat, :sub, :source,
                            ST_SetSRID(ST_GeomFromText(:geom), 4326))
                    """
                ),
                {
                    "osm_id": int(row["osm_id"]) if "osm_id" in gdf.columns and row.get("osm_id") == row.get("osm_id") else None,
                    "name": str(name) if name else None,
                    "cat": category,
                    "sub": subcategory,
                    "source": "OSM/Geofabrik Kosovo clipped to Klina",
                    "geom": geom.wkt,
                },
            )
            n += 1
        upsert_coverage(
            conn,
            "points_of_interest",
            "present" if n else "missing",
            n,
            "OSM/Geofabrik",
            "Amenities/POIs from OSM" if n else "Data unavailable",
        )
    return n


def main() -> None:
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot connect to database: {exc}", file=sys.stderr)
        print("Start PostGIS via `docker compose up -d db` first.", file=sys.stderr)
        raise SystemExit(1)

    print("Importing boundary...")
    print("  boundary:", import_boundary(engine))

    print("Importing settlements...")
    print("  settlements:", import_gpkg(engine, PROCESSED / "settlements.gpkg", "settlements", map_settlements))

    print("Importing buildings...")
    print("  buildings:", import_gpkg(engine, PROCESSED / "buildings.gpkg", "buildings", map_buildings))

    print("Importing roads...")
    print("  roads:", import_gpkg(engine, PROCESSED / "roads.gpkg", "roads", map_roads))

    print("Importing POI...")
    print("  poi:", import_gpkg(engine, PROCESSED / "poi.gpkg", "points_of_interest", map_poi))

    # landuse / water coverage notes if files exist
    with engine.begin() as conn:
        for layer, path in (("landuse", PROCESSED / "landuse.gpkg"), ("water", PROCESSED / "water.gpkg")):
            if path.exists():
                gdf = gpd.read_file(path)
                upsert_coverage(
                    conn,
                    layer,
                    "present" if len(gdf) else "missing",
                    len(gdf),
                    "OSM/Geofabrik",
                    f"Imported from {path.name}" if len(gdf) else "Data unavailable",
                )
            else:
                upsert_coverage(conn, layer, "missing", 0, None, "Data unavailable")
        # demographics never fabricated
        upsert_coverage(
            conn,
            "demographics",
            "missing",
            0,
            None,
            "No open demographics series loaded yet. UI must show Data unavailable.",
        )

    print("Import complete.")


if __name__ == "__main__":
    main()
