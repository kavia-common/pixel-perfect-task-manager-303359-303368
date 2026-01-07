import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _build_default_database_url() -> str:
    """
    Build a default PostgreSQL connection URL for local docker-compose-style setups.

    Priority:
      1) If postgres container env vars are available: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
      2) Otherwise fall back to common defaults.

    Host defaults to 'database' (the docker service name), per user instructions.
    """
    host = os.getenv("POSTGRES_HOST", "database")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


# PUBLIC_INTERFACE
def get_database_url() -> str:
    """Return the DB URL from env (DATABASE_URL) or a safe default to the database container."""
    return os.getenv("DATABASE_URL") or _build_default_database_url()


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


_engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None


# PUBLIC_INTERFACE
def init_engine() -> Engine:
    """
    Initialize and return the SQLAlchemy engine (singleton).

    Uses SQLAlchemy 2.x style engine and psycopg driver.
    """
    global _engine, SessionLocal
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


# PUBLIC_INTERFACE
def get_db() -> Generator:
    """FastAPI dependency that yields a SQLAlchemy session and ensures it is closed."""
    if SessionLocal is None:
        init_engine()
    assert SessionLocal is not None  # for type-checkers
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
