# main.py
import pytest
import logging
#from install_or_update_packages import install_or_update_packages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.base import Base
from src.boxitem import BoxItem
from src.box import Box

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_session():
    """Create a new database session."""
    engine = create_engine('sqlite:///whats_in_the_box.db')  # Using SQLite for local testing
    Base.metadata.create_all(engine)  # Create tables if they don't exist
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture(scope="function")
def session():
    """Create a new in-memory SQLite session for testing."""
    engine = create_engine('sqlite:///:memory:')  # Use in-memory database for tests
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def generate_boxes_and_items(session: Session):
    """Generate 10 boxes and 10 items per box for testing purposes."""
    for i in range(10):
        box = Box(
            box_height=10.0 + i,
            box_length=15.0 + i,
            box_weight=5.0 + i,
            box_location=f"Warehouse Test {i}",
            box_description=f"Box Description {i}"
        )
        box_model = box.add_box(session)

        for j in range(10):
            item = BoxItem(
                box_id=box_model.id,
                item_height=2.5 + j,
                item_length=3.0 + j,
                item_weight=1.0 + j,
                item_location=f"Top Shelf {j}",
                item_description=f"Item {j} in Box {i}"
            )
            item.add_item(session)


def test_find_methods(session: Session):
    """Test find_box and find_boxitem methods."""
    # Generate test data
    generate_boxes_and_items(session)

    # Test finding boxes
    found_boxes = Box.find_box(session, box_location="Warehouse Test 5")
    print(f"Found {len(found_boxes)} boxes matching 'Warehouse Test 5'")

    # Test finding box items
    found_items = BoxItem.find_boxitem(session, item_location="Top Shelf 5")
    print(f"Found {len(found_items)} items matching 'Top Shelf 5'")

    assert len(found_boxes) == 1
    assert len(found_items) == 10

def main():
    # Call the function to install or update the packages
    #print("Starting the package installation or update process...")
    #install_or_update_packages()
    #print("Package installation or update completed.")
    session = create_session()
    generate_boxes_and_items(session)
    test_find_methods(session)

if __name__ == "__main__":
    main()
