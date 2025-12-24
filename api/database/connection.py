"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.config import settings
from api.database.models import Base

# Database URL from settings
DATABASE_URL = settings.database_url

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Dependency function to get database session.

    Yields:
        Database session

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
