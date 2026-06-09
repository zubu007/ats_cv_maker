"""Database setup for authentication and user-owned data."""

from __future__ import annotations

import logging
import os

from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, inspect, text
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


def _switch_to_fallback_database(reason: str) -> None:
    """Switch runtime DB engine/session to sqlite fallback."""
    global DATABASE_URL, engine, SessionLocal
    logger.warning("%s Falling back to sqlite database at %s.", reason, FALLBACK_DATABASE_URL)
    DATABASE_URL = FALLBACK_DATABASE_URL
    engine = _create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


try:
    engine = _create_engine(DATABASE_URL)
except ModuleNotFoundError as exc:
    # Allow local development to continue even if the PostgreSQL driver is missing.
    _switch_to_fallback_database(
        f"Database driver for DATABASE_URL is unavailable ({exc})."
    )

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

    try:
        _ensure_postgres_database_exists()
        _apply_safe_migrations()
        Base.metadata.create_all(bind=engine)
    except (RuntimeError, SQLAlchemyError) as exc:
        if DATABASE_URL.startswith("postgresql"):
            _switch_to_fallback_database(
                "Could not initialize PostgreSQL database "
                f"({type(exc).__name__}: {exc})."
            )
            _apply_safe_migrations()
            Base.metadata.create_all(bind=engine)
            return
        raise


def _apply_safe_migrations() -> None:
    """
    Apply lightweight schema updates for environments without a migration tool.
    """
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "users" in table_names:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "first_name" not in user_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE users ADD COLUMN first_name VARCHAR(120) NOT NULL DEFAULT ''")
                )


def _ensure_postgres_database_exists() -> None:
    """
    Ensure the target PostgreSQL database exists before applying migrations.
    """
    if not DATABASE_URL.startswith("postgresql"):
        return

    target_url = make_url(DATABASE_URL)
    target_database = target_url.database

    if not target_database:
        return

    maintenance_url = target_url.set(database="postgres")

    maintenance_engine = create_engine(
        maintenance_url,
        future=True,
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

    quoted_database_name = target_database.replace('"', '""')

    try:
        with maintenance_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": target_database},
            ).scalar()

            if not exists:
                connection.execute(text(f'CREATE DATABASE "{quoted_database_name}"'))
                logger.info("Created PostgreSQL database '%s'.", target_database)
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Could not connect to PostgreSQL to initialize database. "
            "Verify DATABASE_URL, credentials, and that PostgreSQL is running."
        ) from exc
    finally:
        maintenance_engine.dispose()
