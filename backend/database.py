"""
Database connection and session manager.
Supports PostgreSQL with fallback to SQLite for local development.
"""

import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve absolute path for local SQLite database file to avoid working-directory discrepancies
BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_SQLITE_URL = f"sqlite:///{BASE_DIR / 'hirewise.db'}"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_SQLITE_URL
)

# SQLite requires check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Dependency for providing SQLAlchemy DB session in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
