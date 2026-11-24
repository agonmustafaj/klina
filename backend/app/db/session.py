from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db() -> dict:
    """Return DB health details without raising to the caller."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            postgis = conn.execute(text("SELECT PostGIS_Version()")).scalar()
        return {"ok": True, "postgis": postgis}
    except Exception as exc:  # noqa: BLE001 — health endpoint must not crash
        return {"ok": False, "error": str(exc)}
