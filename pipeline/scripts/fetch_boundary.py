#!/usr/bin/env python3
"""Fetch and verify the Municipality of Klina (Klinë) admin boundary from OSM.

Source of truth: OpenStreetMap administrative boundary via Nominatim.
Never invents geometry — fails loudly if a verified polygon cannot be obtained.

Usage:
  python pipeline/scripts/fetch_boundary.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "boundary"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Known OSM relation for Komuna e Klinës / Opština Klina (admin boundary).
# Cross-checked via Nominatim (class=boundary, type=administrative).
KNOWN_RELATION_ID = 1332179

NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
NOMINATIM_LOOKUP = "https://nominatim.openstreetmap.org/lookup"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "CityOS-Klina/0.1 (digital-twin; research)"}

# Reference municipal area ~308.8 km² — allow OSM variance.
AREA_MIN_KM2 = 250.0
AREA_MAX_KM2 = 380.0


def _is_admin_polygon(hit: dict) -> bool:
    if hit.get("osm_type") != "relation":
        return False
    if hit.get("class") not in ("boundary", "place"):
        return False
    geom = hit.get("geojson") or {}
    return geom.get("type") in ("Polygon", "MultiPolygon")


def nominatim_search() -> list[dict]:
    queries = [
        {"q": "Komuna e Klinës", "format": "json", "polygon_geojson": 1, "limit": 10},
        {
            "q": "Komuna e Klinës / Opština Klina",
            "format": "json",
            "polygon_geojson": 1,
            "limit": 10,
        },
        {
            "q": "Klina Municipality Kosovo",
            "format": "json",
            "polygon_geojson": 1,
            "limit": 10,
            "featureType": "settlement",
        },
    ]
    hits: list[dict] = []
    for params in queries:
        r = requests.get(NOMINATIM_SEARCH, params=params, headers=UA, timeout=60)
        r.raise_for_status()
        hits.extend(r.json())
    return hits


def nominatim_lookup_relation(relation_id: int) -> dict | None:
    r = requests.get(
        NOMINATIM_LOOKUP,
        params={"osm_ids": f"R{relation_id}", "format": "json", "polygon_geojson": 1},
        headers=UA,
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data[0] if data else None


def overpass_tags(relation_id: int) -> dict:
    query = f"""
    [out:json][timeout:60];
    relation({relation_id});
    out tags bb;
    """
    r = requests.post(OVERPASS_URL, data={"data": query}, timeout=90)
    if r.status_code != 200:
        return {}
    elements = r.json().get("elements") or []
    return (elements[0].get("tags") or {}) if elements else {}


def verify_area_km2(geometry: dict) -> float | None:
    try:
        import pyproj
        from shapely.geometry import shape
        from shapely.ops import transform

        geom = shape(geometry)
        project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32634", always_xy=True).transform
        return transform(project, geom).area / 1_000_000.0
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: could not compute area: {exc}", file=sys.stderr)
        return None


def choose_boundary() -> tuple[dict, dict]:
    # 1) Prefer known relation lookup
    known = nominatim_lookup_relation(KNOWN_RELATION_ID)
    candidates: list[dict] = []
    if known and _is_admin_polygon(known):
        candidates.append(known)

    # 2) Search results — relations with polygon only
    for hit in nominatim_search():
        if _is_admin_polygon(hit):
            candidates.append(hit)

    # Deduplicate by osm_id
    seen: set[int] = set()
    unique: list[dict] = []
    for c in candidates:
        oid = int(c["osm_id"])
        if oid in seen:
            continue
        seen.add(oid)
        unique.append(c)

    if not unique:
        raise SystemExit(
            "ERROR: No OSM administrative polygon for Klina municipality. "
            "Refusing to fabricate a boundary."
        )

    # Prefer known ID, else first admin boundary
    chosen = next((c for c in unique if int(c["osm_id"]) == KNOWN_RELATION_ID), unique[0])

    if not _is_admin_polygon(chosen):
        raise SystemExit("ERROR: Chosen Nominatim hit is not an admin polygon. Refusing to use it.")

    area = verify_area_km2(chosen["geojson"])
    if area is None:
        raise SystemExit("ERROR: Could not compute boundary area for verification.")
    if not (AREA_MIN_KM2 <= area <= AREA_MAX_KM2):
        raise SystemExit(
            f"ERROR: Boundary area {area:.1f} km² outside expected range "
            f"[{AREA_MIN_KM2}, {AREA_MAX_KM2}] (~308.8 km²). Refusing to accept."
        )

    tags = {}
    try:
        tags = overpass_tags(int(chosen["osm_id"]))
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Overpass tag check failed: {exc}", file=sys.stderr)

    if tags:
        print(
            f"Overpass tags: name={tags.get('name')} "
            f"admin_level={tags.get('admin_level')} boundary={tags.get('boundary')}"
        )
        if tags.get("boundary") and tags.get("boundary") != "administrative":
            raise SystemExit(f"ERROR: unexpected boundary tag {tags.get('boundary')}")
        if tags.get("admin_level") and tags.get("admin_level") not in ("6", "7", "8"):
            raise SystemExit(f"ERROR: unexpected admin_level={tags.get('admin_level')}")

    meta = {
        "source": "OpenStreetMap via Nominatim",
        "source_url": "https://nominatim.openstreetmap.org/",
        "osm_type": chosen.get("osm_type"),
        "osm_id": chosen.get("osm_id"),
        "display_name": chosen.get("display_name"),
        "boundingbox": chosen.get("boundingbox"),
        "licence": chosen.get("licence"),
        "class": chosen.get("class"),
        "type": chosen.get("type"),
        "area_km2_computed": round(area, 2),
        "area_km2_reference": 308.8,
        "overpass_tags": tags or None,
        "verification": "admin polygon + area within municipal reference range",
    }
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Klina",
                    "name_local": "Klinë",
                    "osm_type": "relation",
                    "osm_id": chosen.get("osm_id"),
                    "osm_relation_id": chosen.get("osm_id"),
                    "source": meta["source"],
                    "source_url": meta["source_url"],
                    "display_name": meta["display_name"],
                    "area_km2_computed": round(area, 2),
                },
                "geometry": chosen["geojson"],
            }
        ],
    }
    print(f"Verified area ≈ {area:.1f} km² (reference ~308.8 km²)")
    return fc, meta


def main() -> None:
    print("Fetching Klina municipal boundary from Nominatim (OSM)...")
    fc, meta = choose_boundary()
    geo_path = OUT_DIR / "klina_boundary.geojson"
    meta_path = OUT_DIR / "klina_boundary.meta.json"
    geo_path.write_text(json.dumps(fc, indent=2), encoding="utf-8")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote {geo_path}")
    print(f"Wrote {meta_path}")
    print("Boundary acquisition complete — real OSM geometry only.")


if __name__ == "__main__":
    main()
