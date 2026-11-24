"""PostGIS-backed geographic entities for Klina municipality.

All geometries must originate from verified open sources (OSM/Geofabrik etc.).
Never insert fabricated features.
"""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MunicipalBoundary(Base):
    __tablename__ = "municipal_boundary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(128))
    osm_relation_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    source: Mapped[str] = mapped_column(String(256), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    area_km2: Mapped[float | None] = mapped_column(Float)
    geom: Mapped[object] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    name_local: Mapped[str | None] = mapped_column(String(256))
    place_type: Mapped[str | None] = mapped_column(String(64))
    population: Mapped[int | None] = mapped_column(Integer)  # only if present in source
    source: Mapped[str] = mapped_column(String(256), nullable=False)
    geom: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    building_type: Mapped[str | None] = mapped_column(String(128))
    name: Mapped[str | None] = mapped_column(String(256))
    levels: Mapped[int | None] = mapped_column(Integer)
    height_m: Mapped[float | None] = mapped_column(Float)
    has_3d: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source: Mapped[str] = mapped_column(String(256), nullable=False)
    geom: Mapped[object] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    name: Mapped[str | None] = mapped_column(String(256))
    highway: Mapped[str | None] = mapped_column(String(64), index=True)
    surface: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(256), nullable=False)
    geom: Mapped[object] = mapped_column(Geometry("MULTILINESTRING", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PointOfInterest(Base):
    __tablename__ = "points_of_interest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    name: Mapped[str | None] = mapped_column(String(256), index=True)
    category: Mapped[str | None] = mapped_column(String(128), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(128))
    source: Mapped[str] = mapped_column(String(256), nullable=False)
    geom: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DataCoverage(Base):
    """Tracks which datasets are present so the UI never fakes coverage."""

    __tablename__ = "data_coverage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    layer: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # present | partial | missing
    feature_count: Mapped[int | None] = mapped_column(Integer)
    has_3d: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source: Mapped[str | None] = mapped_column(String(256))
    source_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
