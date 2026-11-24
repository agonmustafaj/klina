from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import check_db
from app.schemas.geo import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    db = check_db()
    return HealthResponse(
        status="ok" if db.get("ok") else "degraded",
        environment=settings.environment,
        database=db,
    )
