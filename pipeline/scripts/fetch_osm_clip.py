#!/usr/bin/env python3
"""Download Geofabrik Kosovo extract and clip to the verified Klina boundary.

Requires: verified boundary at data/boundary/klina_boundary.geojson
Optional tools: osmium-tool (preferred), or falls back to GeoPandas pyogrio clip of .osm.pbf layers.

Usage:
  python pipeline/scripts/fetch_osm_clip.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
BOUNDARY = ROOT / "data" / "boundary" / "klina_boundary.geojson"

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

GEOFABRIK_URL = "https://download.geofabrik.de/europe/kosovo-latest.osm.pbf"
PBF_PATH = RAW / "kosovo-latest.osm.pbf"
CLIPPED_PBF = PROCESSED / "klina.osm.pbf"
MANIFEST = PROCESSED / "acquisition_manifest.json"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def download_pbf() -> None:
    if PBF_PATH.exists() and PBF_PATH.stat().st_size > 1_000_000:
        print(f"Using existing {PBF_PATH} ({PBF_PATH.stat().st_size} bytes)")
        return
    print(f"Downloading {GEOFABRIK_URL} ...")
    with requests.get(GEOFABRIK_URL, stream=True, timeout=600) as r:
        r.raise_for_status()
        tmp = PBF_PATH.with_suffix(".partial")
        with tmp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
        tmp.replace(PBF_PATH)
    print(f"Downloaded {PBF_PATH} ({PBF_PATH.stat().st_size} bytes)")


def boundary_poly_for_osmium() -> Path:
    """Write .poly file for osmium extract from GeoJSON boundary."""
    import geopandas as gpd

    gdf = gpd.read_file(BOUNDARY)
    if gdf.empty:
        raise SystemExit("ERROR: empty boundary GeoJSON")
    geom = gdf.union_all()
    poly_path = PROCESSED / "klina.poly"
    # .poly format: https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
    lines = ["klina", "1"]
    if geom.geom_type == "MultiPolygon":
        polys = list(geom.geoms)
    else:
        polys = [geom]
    for i, poly in enumerate(polys, start=1):
        if i > 1:
            lines.append(str(i))
        for x, y in poly.exterior.coords:
            lines.append(f"  {x} {y}")
        lines.append("END")
    lines.append("END")
    poly_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return poly_path


def clip_with_osmium(poly_path: Path) -> bool:
    import shutil

    # Use shutil.which — `which` is Unix-only and crashes on Windows.
    if shutil.which("osmium") is None:
        return False
    cmd = [
        "osmium",
        "extract",
        "-p",
        str(poly_path),
        str(PBF_PATH),
        "-o",
        str(CLIPPED_PBF),
        "--overwrite",
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return True


def clip_layers_geopandas() -> dict:
    """Fallback: read key layers from PBF via pyogrio and clip to boundary."""
    import geopandas as gpd

    boundary = gpd.read_file(BOUNDARY).to_crs(4326)
    clip_geom = boundary.union_all()
    layers_out = {}

    # pyogrio can list layers in osm.pbf
    try:
        import pyogrio

        layer_names = [n for n, *_ in pyogrio.list_layers(PBF_PATH)]
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: could not list PBF layers: {exc}", file=sys.stderr)
        layer_names = ["points", "lines", "multipolygons"]

    interesting = {
        "points": "points",
        "lines": "lines",
        "multilinestrings": "multilinestrings",
        "multipolygons": "multipolygons",
        "other_relations": "other_relations",
    }
    for layer in layer_names:
        key = interesting.get(layer)
        if not key:
            continue
        print(f"Reading & clipping layer: {layer}")
        try:
            gdf = gpd.read_file(PBF_PATH, layer=layer)
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {layer}: {exc}")
            continue
        if gdf.empty or gdf.geometry is None:
            continue
        gdf = gdf.set_crs(4326, allow_override=True)
        try:
            clipped = gdf[gdf.intersects(clip_geom)].copy()
            clipped["geometry"] = clipped.geometry.intersection(clip_geom)
            clipped = clipped[~clipped.geometry.is_empty]
        except Exception as exc:  # noqa: BLE001
            print(f"  clip failed for {layer}: {exc}")
            continue
        out = PROCESSED / f"klina_{key}.gpkg"
        clipped.to_file(out, driver="GPKG")
        layers_out[key] = {"path": str(out.relative_to(ROOT)), "count": len(clipped)}
        print(f"  wrote {out} ({len(clipped)} features)")
    return layers_out


def extract_thematic_layers() -> dict:
    """From clipped geopackages (or full clip), derive buildings/roads/places/amenities."""
    import geopandas as gpd

    boundary = gpd.read_file(BOUNDARY).to_crs(4326)
    clip_geom = boundary.union_all()
    result = {}

    multi = PROCESSED / "klina_multipolygons.gpkg"
    lines = PROCESSED / "klina_lines.gpkg"
    points = PROCESSED / "klina_points.gpkg"

    # If osmium produced only PBF, try reading clipped PBF
    source_multi = multi if multi.exists() else None
    source_lines = lines if lines.exists() else None
    source_points = points if points.exists() else None

    if CLIPPED_PBF.exists() and not (source_multi and source_lines):
        try:
            gdf = gpd.read_file(CLIPPED_PBF, layer="multipolygons")
            gdf = gdf.set_crs(4326, allow_override=True)
            gdf.to_file(multi, driver="GPKG")
            source_multi = multi
        except Exception as exc:  # noqa: BLE001
            print(f"multipolygons from clipped pbf: {exc}")
        try:
            gdf = gpd.read_file(CLIPPED_PBF, layer="lines")
            gdf = gdf.set_crs(4326, allow_override=True)
            gdf.to_file(lines, driver="GPKG")
            source_lines = lines
        except Exception as exc:  # noqa: BLE001
            print(f"lines from clipped pbf: {exc}")
        try:
            gdf = gpd.read_file(CLIPPED_PBF, layer="points")
            gdf = gdf.set_crs(4326, allow_override=True)
            gdf.to_file(points, driver="GPKG")
            source_points = points
        except Exception as exc:  # noqa: BLE001
            print(f"points from clipped pbf: {exc}")

    def save_subset(gdf, mask, name):
        sub = gdf[mask].copy()
        if sub.empty:
            print(f"  {name}: 0 features (Data unavailable in OSM clip)")
            result[name] = {"count": 0, "path": None}
            return
        out = PROCESSED / f"{name}.gpkg"
        sub.to_file(out, driver="GPKG")
        result[name] = {"count": len(sub), "path": str(out.relative_to(ROOT))}
        print(f"  {name}: {len(sub)} → {out}")

    if source_multi and source_multi.exists():
        mp = gpd.read_file(source_multi)
        if "building" in mp.columns:
            save_subset(mp, mp["building"].notna() & (mp["building"] != ""), "buildings")
        if "landuse" in mp.columns:
            save_subset(mp, mp["landuse"].notna(), "landuse")
        if "natural" in mp.columns or "waterway" in mp.columns or "water" in mp.columns:
            water_mask = False
            if "natural" in mp.columns:
                water_mask = water_mask | (mp["natural"] == "water")
            if "water" in mp.columns:
                water_mask = water_mask | mp["water"].notna()
            save_subset(mp, water_mask, "water")

    if source_lines and source_lines.exists():
        ln = gpd.read_file(source_lines)
        if "highway" in ln.columns:
            save_subset(ln, ln["highway"].notna(), "roads")

    if source_points and source_points.exists():
        import re

        pt = gpd.read_file(source_points)
        if "place" in pt.columns:
            save_subset(pt, pt["place"].notna(), "settlements")
        amenity_keys = ("amenity", "shop", "tourism", "healthcare", "office")
        amenity_cols = [c for c in amenity_keys if c in pt.columns]
        if amenity_cols:
            mask = False
            for c in amenity_cols:
                mask = mask | pt[c].notna()
            save_subset(pt, mask, "poi")
        elif "other_tags" in pt.columns:
            # GDAL OSM driver often packs amenities into other_tags HSTORE text
            rows = []
            for _, row in pt.iterrows():
                tags = row.get("other_tags")
                if not isinstance(tags, str):
                    continue
                found = {}
                for k in amenity_keys:
                    m = re.search(rf'"{k}"=>"([^"]+)"', tags)
                    if m:
                        found[k] = m.group(1)
                if found:
                    d = row.to_dict()
                    d.update(found)
                    rows.append(d)
            if rows:
                poi = gpd.GeoDataFrame(rows, geometry="geometry", crs=pt.crs)
                out = PROCESSED / "poi.gpkg"
                poi.to_file(out, driver="GPKG")
                result["poi"] = {"count": len(poi), "path": str(out.relative_to(ROOT))}
                print(f"  poi: {len(poi)} → {out}")
            else:
                result["poi"] = {"count": 0, "path": None}
                print("  poi: 0 features (Data unavailable in OSM clip)")


    # Always keep boundary copy in processed
    boundary.to_file(PROCESSED / "boundary.gpkg", driver="GPKG")
    result["boundary"] = {"count": len(boundary), "path": "data/processed/boundary.gpkg"}
    return result


def main() -> None:
    if not BOUNDARY.exists():
        raise SystemExit(
            f"ERROR: missing {BOUNDARY}. Run fetch_boundary.py first. Refusing to invent a clip region."
        )

    download_pbf()
    checksum = sha256_file(PBF_PATH)

    poly = boundary_poly_for_osmium()
    used_osmium = False
    try:
        used_osmium = clip_with_osmium(poly)
    except (subprocess.CalledProcessError, OSError, FileNotFoundError) as exc:
        print(f"osmium extract unavailable/failed: {exc}", file=sys.stderr)
        used_osmium = False

    layer_stats = {}
    if not used_osmium:
        print("osmium not available — falling back to GeoPandas/pyogrio clip")
        layer_stats = clip_layers_geopandas()
    else:
        print(f"Clipped PBF written to {CLIPPED_PBF}")

    thematic = extract_thematic_layers()

    manifest = {
        "municipality": "Klina",
        "geofabrik_url": GEOFABRIK_URL,
        "raw_pbf": str(PBF_PATH.relative_to(ROOT)),
        "raw_pbf_sha256": checksum,
        "raw_pbf_bytes": PBF_PATH.stat().st_size,
        "boundary": str(BOUNDARY.relative_to(ROOT)),
        "clip_method": "osmium" if used_osmium else "geopandas",
        "clipped_pbf": str(CLIPPED_PBF.relative_to(ROOT)) if CLIPPED_PBF.exists() else None,
        "osm_layers": layer_stats,
        "thematic_layers": thematic,
        "notes": (
            "All geometries are clipped from Geofabrik Kosovo OSM extract "
            "to the verified municipal boundary. No features were fabricated."
        ),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
