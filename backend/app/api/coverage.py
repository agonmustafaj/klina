from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.geo import DataCoverage
from app.schemas.geo import CoverageItem, CoverageResponse, LayerMeta, LayersListResponse

router = APIRouter(prefix="/api/v1", tags=["coverage"])

# Declared layers CityOS expects. Status stays "missing" until real import runs.
EXPECTED_LAYERS = [
    "municipal_boundary",
    "settlements",
    "buildings",
    "roads",
    "points_of_interest",
    "landuse",
    "water",
    "demographics",
    "3d_buildings",
]


@router.get("/coverage", response_model=CoverageResponse)
def get_coverage(db: Session = Depends(get_db)) -> CoverageResponse:
    try:
        rows = db.query(DataCoverage).all()
    except Exception:  # noqa: BLE001
        rows = []

    by_layer = {r.layer: r for r in rows}
    items: list[CoverageItem] = []
    for layer in EXPECTED_LAYERS:
        row = by_layer.get(layer)
        if row:
            items.append(
                CoverageItem(
                    layer=row.layer,
                    status=row.status,
                    feature_count=row.feature_count,
                    has_3d=row.has_3d,
                    source=row.source,
                    source_url=row.source_url,
                    notes=row.notes,
                    updated_at=row.updated_at,
                )
            )
        else:
            items.append(
                CoverageItem(
                    layer=layer,
                    status="missing",
                    feature_count=None,
                    has_3d=False,
                    notes="Not yet imported. Data unavailable.",
                )
            )

    present = sum(1 for i in items if i.status == "present")
    message = None
    if present == 0:
        message = "No geographic layers imported yet. Run the Phase 2 pipeline to load OSM data."

    return CoverageResponse(items=items, message=message)


@router.get("/layers", response_model=LayersListResponse)
def list_layers(db: Session = Depends(get_db)) -> LayersListResponse:
    coverage = get_coverage(db)
    return LayersListResponse(
        layers=[
            LayerMeta(
                name=i.layer,
                status=i.status,
                feature_count=i.feature_count,
                has_3d=i.has_3d,
            )
            for i in coverage.items
        ]
    )
