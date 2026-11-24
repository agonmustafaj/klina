from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str = "cityos-api"
    environment: str
    database: dict


class CoverageItem(BaseModel):
    layer: str
    status: str
    feature_count: int | None = None
    has_3d: bool = False
    source: str | None = None
    source_url: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class CoverageResponse(BaseModel):
    municipality: str = "Klina"
    items: list[CoverageItem]
    message: str | None = Field(
        default=None,
        description="Human-readable note when coverage is empty or incomplete",
    )


class LayerMeta(BaseModel):
    name: str
    status: str
    feature_count: int | None = None
    has_3d: bool = False


class LayersListResponse(BaseModel):
    layers: list[LayerMeta]
