# tests/conftest.py
import sys
print(sys.path)
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

# Make sure src is added to sys.path for pytest
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

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
