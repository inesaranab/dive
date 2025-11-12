"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from app.config import settings

# Base class for models
Base = declarative_base()


# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


@contextmanager
def get_db() -> Session:
    """Get database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session():
    """Dependency for FastAPI endpoints to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

