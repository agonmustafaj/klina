from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import coverage, geo, health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    description=(
        "CityOS API — Digital Twin of the Municipality of Klina. "
        "All geographic features come from verified open sources. "
        "Missing layers return empty FeatureCollections / Data unavailable."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(coverage.router)
app.include_router(geo.router)


@app.get("/")
def root() -> dict:
    return {
        "service": "CityOS",
        "municipality": "Klina",
        "docs": "/docs",
        "health": "/health",
    }
