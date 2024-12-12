# src/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.base import Base
from src.utils.platform_utils import get_database_path
import logging
Logger = logging.getLogger(__name__)

# Create the engine and session factory
database_file = get_database_path()
DATABASE_URL = f'sqlite:///{database_file}'

Logger.debug(f"database.py: Using database at {DATABASE_URL}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory for creating new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database by creating tables if they don't exist."""
    Logger.debug("database.py: init_db() called")
    # Check if database file exists (only relevant for SQLite)
    if engine.url.drivername == 'sqlite':
        database_file = engine.url.database
        Logger.debug(f"database.py: Checking if database file exists at {database_file}")
        if not os.path.exists(database_file):
            Logger.info("Database file not found. Creating new database and tables.")
            Base.metadata.create_all(bind=engine)
        else:
            Logger.debug("Database file exists. Ensuring all tables are created.")
            Base.metadata.create_all(bind=engine)
    else:
        # For other databases, we can directly create all tables
        Base.metadata.create_all(bind=engine)
