# tests/conftest.py
import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.models import Base

@pytest.fixture(scope="function")
def session():
    """Create a new in-memory SQLite session for testing."""
    engine = create_engine('sqlite:///:memory:')  # In-memory database for testing
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def box_attributes():
    """Provide default box attributes."""
    return {
        "box_height": 10.0,
        "box_length": 15.0,
        "box_weight": 5.0,
        "box_location": "Warehouse Test",
        "box_description": "Test Box",
    }

@pytest.fixture
def box_item_attributes():
    """Provide default box item attributes."""
    return {
        "item_height": 2.5,
        "item_length": 3.0,
        "item_weight": 1.0,
        "item_location": "Top Shelf",
        "item_description": "Test Item",
    }
