"""GeoJSON layer endpoints.

Return empty FeatureCollections when data is not yet imported.
Never fabricate features.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from geoalchemy2.functions import ST_AsGeoJSON, ST_Intersects, ST_MakeEnvelope
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.geo import Building, MunicipalBoundary, PointOfInterest, Road, Settlement

router = APIRouter(prefix="/api/v1/geo", tags=["geo"])


def _empty_fc(message: str = "Data unavailable") -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [],
        "properties": {"message": message},
    }


def _rows_to_fc(rows: list[tuple], props_keys: list[str]) -> dict[str, Any]:
    features = []
    for row in rows:
        # last column is geojson string from ST_AsGeoJSON
        *prop_vals, geom_json = row
        import json

        geometry = json.loads(geom_json) if geom_json else None
        properties = {k: v for k, v in zip(props_keys, prop_vals, strict=True)}
        features.append({"type": "Feature", "geometry": geometry, "properties": properties})
    return {"type": "FeatureCollection", "features": features}


@router.get("/boundary")
def get_boundary(db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        rows = (
            db.query(
                MunicipalBoundary.id,
                MunicipalBoundary.name,
                MunicipalBoundary.name_local,
                MunicipalBoundary.osm_relation_id,
                MunicipalBoundary.source,
                MunicipalBoundary.area_km2,
                ST_AsGeoJSON(MunicipalBoundary.geom),
            )
            .limit(1)
            .all()
        )
    except Exception:  # noqa: BLE001
        return _empty_fc("Municipal boundary not loaded. Data unavailable.")

    if not rows:
        return _empty_fc("Municipal boundary not loaded. Data unavailable.")

    return _rows_to_fc(
        rows,
        ["id", "name", "name_local", "osm_relation_id", "source", "area_km2"],
    )


@router.get("/settlements")
def get_settlements(
    db: Session = Depends(get_db),
    bbox: str | None = Query(None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    try:
        q = db.query(
            Settlement.id,
            Settlement.osm_id,
            Settlement.name,
            Settlement.name_local,
            Settlement.place_type,
            Settlement.population,
            Settlement.source,
            ST_AsGeoJSON(Settlement.geom),
        )
        if bbox:
            parts = [float(x) for x in bbox.split(",")]
            if len(parts) == 4:
                env = ST_MakeEnvelope(parts[0], parts[1], parts[2], parts[3], 4326)
                q = q.filter(ST_Intersects(Settlement.geom, env))
        rows = q.order_by(Settlement.name).offset(offset).limit(limit).all()
    except Exception:  # noqa: BLE001
        return _empty_fc("Settlements not loaded. Data unavailable.")

    if not rows:
        return _empty_fc("Settlements not loaded. Data unavailable.")

    return _rows_to_fc(
        rows,
        ["id", "osm_id", "name", "name_local", "place_type", "population", "source"],
    )


@router.get("/buildings")
def get_buildings(
    db: Session = Depends(get_db),
    bbox: str | None = Query(None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    try:
        q = db.query(
            Building.id,
            Building.osm_id,
            Building.building_type,
            Building.name,
            Building.levels,
            Building.height_m,
            Building.has_3d,
            Building.source,
            ST_AsGeoJSON(Building.geom),
        )
        if bbox:
            parts = [float(x) for x in bbox.split(",")]
            if len(parts) == 4:
                env = ST_MakeEnvelope(parts[0], parts[1], parts[2], parts[3], 4326)
                q = q.filter(ST_Intersects(Building.geom, env))
        rows = q.offset(offset).limit(limit).all()
    except Exception:  # noqa: BLE001
        return _empty_fc("Buildings not loaded. Data unavailable.")

    if not rows:
        return _empty_fc("Buildings not loaded. Data unavailable.")

    return _rows_to_fc(
        rows,
        ["id", "osm_id", "building_type", "name", "levels", "height_m", "has_3d", "source"],
    )


@router.get("/roads")
def get_roads(
    db: Session = Depends(get_db),
    bbox: str | None = Query(None, description="minLon,minLat,maxLon,maxLat"),
    limit: int = Query(2000, ge=1, le=20000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    try:
        q = db.query(
            Road.id,
            Road.osm_id,
            Road.name,
            Road.highway,
            Road.surface,
            Road.source,
            ST_AsGeoJSON(Road.geom),
        )
        if bbox:
            parts = [float(x) for x in bbox.split(",")]
            if len(parts) == 4:
                env = ST_MakeEnvelope(parts[0], parts[1], parts[2], parts[3], 4326)
                q = q.filter(ST_Intersects(Road.geom, env))
        rows = q.offset(offset).limit(limit).all()
    except Exception:  # noqa: BLE001
        return _empty_fc("Roads not loaded. Data unavailable.")

    if not rows:
        return _empty_fc("Roads not loaded. Data unavailable.")

    return _rows_to_fc(rows, ["id", "osm_id", "name", "highway", "surface", "source"])


@router.get("/poi")
def get_poi(
    db: Session = Depends(get_db),
    bbox: str | None = Query(None, description="minLon,minLat,maxLon,maxLat"),
    category: str | None = None,
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    try:
        q = db.query(
            PointOfInterest.id,
            PointOfInterest.osm_id,
            PointOfInterest.name,
            PointOfInterest.category,
            PointOfInterest.subcategory,
            PointOfInterest.source,
            ST_AsGeoJSON(PointOfInterest.geom),
        )
        if category:
            q = q.filter(PointOfInterest.category == category)
        if bbox:
            parts = [float(x) for x in bbox.split(",")]
            if len(parts) == 4:
                env = ST_MakeEnvelope(parts[0], parts[1], parts[2], parts[3], 4326)
                q = q.filter(ST_Intersects(PointOfInterest.geom, env))
        rows = q.offset(offset).limit(limit).all()
    except Exception:  # noqa: BLE001
        return _empty_fc("Points of interest not loaded. Data unavailable.")

    if not rows:
        return _empty_fc("Points of interest not loaded. Data unavailable.")

    return _rows_to_fc(
        rows,
        ["id", "osm_id", "name", "category", "subcategory", "source"],
    )


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(25, ge=1, le=100),
) -> dict[str, Any]:
    """Search settlements and POIs by name. Empty results are valid — never invent matches."""
    pattern = f"%{q}%"
    results: list[dict[str, Any]] = []
    try:
        settlements = (
            db.query(Settlement.id, Settlement.name, Settlement.place_type, ST_AsGeoJSON(Settlement.geom))
            .filter(Settlement.name.ilike(pattern))
            .limit(limit)
            .all()
        )
        import json

        for s in settlements:
            results.append(
                {
                    "type": "settlement",
                    "id": s[0],
                    "name": s[1],
                    "place_type": s[2],
                    "geometry": json.loads(s[3]) if s[3] else None,
                }
            )
        remaining = max(0, limit - len(results))
        if remaining:
            pois = (
                db.query(
                    PointOfInterest.id,
                    PointOfInterest.name,
                    PointOfInterest.category,
                    ST_AsGeoJSON(PointOfInterest.geom),
                )
                .filter(PointOfInterest.name.ilike(pattern))
                .limit(remaining)
                .all()
            )
            for p in pois:
                results.append(
                    {
                        "type": "poi",
                        "id": p[0],
                        "name": p[1],
                        "category": p[2],
                        "geometry": json.loads(p[3]) if p[3] else None,
                    }
                )
    except Exception:  # noqa: BLE001
        return {"query": q, "results": [], "message": "Search unavailable until data is imported."}

    return {
        "query": q,
        "results": results,
        "message": None if results else "No matches. Data unavailable or query unmatched.",
    }


@router.get("/stats/summary")
def stats_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Counts from imported tables only — returns unavailable when empty."""
    try:
        counts = {}
        for label, table in [
            ("settlements", "settlements"),
            ("buildings", "buildings"),
            ("roads", "roads"),
            ("points_of_interest", "points_of_interest"),
        ]:
            counts[label] = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        if all(v == 0 for v in counts.values()):
            return {"status": "unavailable", "message": "Data unavailable", "counts": counts}
        return {"status": "ok", "counts": counts}
    except Exception as exc:  # noqa: BLE001
        return {"status": "unavailable", "message": "Data unavailable", "error": str(exc)}
