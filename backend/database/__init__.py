"""
Database module for Dita backend.
Handles database connection, session management, and base model.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dita_user:dita_password@localhost:5432/dita_db")

# Create engine with lazy initialization
engine = None
SessionLocal = None

def init_db():
    """Initialize database engine and session maker."""
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields database session and ensures it's closed after use.
    """
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
