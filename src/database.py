# src/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.base import Base
import src.models  # Import models so that SQLAlchemy knows about them

# Create the engine and session factory
DATABASE_URL = 'sqlite:///./whats_in_the_box.db'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory for creating new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database by creating tables if they don't exist."""
    # Check if database file exists (only relevant for SQLite)
    if engine.url.drivername == 'sqlite':
        database_file = engine.url.database
        if not os.path.exists(database_file):
            print("Database file not found. Creating new database and tables.")
            Base.metadata.create_all(bind=engine)
        else:
            Base.metadata.create_all(bind=engine)
    else:
        # For other databases, we can directly create all tables
        Base.metadata.create_all(bind=engine)
