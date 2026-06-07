"""Database setup for authentication and user-owned data."""

from __future__ import annotations

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ats_cv_maker"
FALLBACK_DATABASE_URL = "sqlite:///./ats_cv_maker.db"


def _create_engine(database_url: str):
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        database_url,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

try:
    engine = _create_engine(DATABASE_URL)
except ModuleNotFoundError as exc:
    # Allow local development to continue even if the PostgreSQL driver is missing.
    logger.warning(
        "Database driver for DATABASE_URL is unavailable (%s). Falling back to sqlite.",
        exc,
    )
    DATABASE_URL = FALLBACK_DATABASE_URL
    engine = _create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """Yield a SQLAlchemy session for request handling."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all configured tables if they do not already exist."""
    from . import db_models  # pylint: disable=unused-import

    Base.metadata.create_all(bind=engine)
