# tests/unit/test_box.py
import sys
from src.box import Box
from src.boxitem import BoxItem
from src.models import BoxModel, BoxItemModel
from sqlalchemy.orm import Session

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
    print(sys.path)
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

def test_add_box(session, box_attributes):
    """Test adding a new box to the database."""
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Query to verify the box was added
    added_box = session.query(BoxModel).filter_by(box_location="Warehouse Test").first()

    assert box_model == added_box  # returned box model is same as queried one
    assert added_box is not None
    assert added_box.box_height == 10.0
    assert added_box.box_length == 15.0
    assert added_box.box_weight == 5.0
    assert added_box.box_location == "Warehouse Test"
    assert added_box.box_description == "Test Box"
    assert len(added_box.box_QRcode) == 10

def test_edit_box(session, box_attributes):
    """Test editing an existing box."""
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Edit the box's location and description
    box.edit_box(session, box_location="Updated Warehouse", box_description="Updated description")

    # Query to verify the box was edited
    edited_box = session.query(BoxModel).filter_by(box_location="Updated Warehouse").first()

    assert box_model == edited_box
    assert edited_box is not None
    assert edited_box.box_location == "Updated Warehouse"
    assert edited_box.box_description == "Updated description"

def test_delete_box(session, box_attributes):
    """Test deleting a box from the database."""
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Delete the box
    box.delete_box(session)

    # Query to verify the box was deleted
    deleted_box = session.query(BoxModel).filter_by(box_location="Warehouse Test").first()

    assert deleted_box is None

def test_unique_qr_code_generation(session, box_attributes):
    """Test that each box gets a unique QR code."""
    box1 = Box(**box_attributes)
    box2 = Box(**box_attributes)

    box1.add_box(session)
    box2.add_box(session)

    # Ensure the QR codes are unique
    assert box1.box_QRcode != box2.box_QRcode
    assert len(box1.box_QRcode) == 10  # Check length of the QR code
    assert len(box2.box_QRcode) == 10  # Check length of the QR code

def test_add_box_item(session, box_attributes, box_item_attributes):
    """Test adding a new item to a box in the database."""
    # Add a box first
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Create and add a new BoxItem linked to the box
    item = BoxItem(box_id=box_model.id, **box_item_attributes)
    box_model_item = item.add_item(session)

    # Query to verify the item was added
    added_item = session.query(BoxItemModel).filter_by(item_description="Test Item").first()

    assert added_item is not None
    assert added_item.item_height == 2.5
    assert added_item.item_length == 3.0
    assert added_item.item_weight == 1.0
    assert added_item.item_location == "Top Shelf"
    assert added_item.item_description == "Test Item"
    assert added_item.box_id == box_model.id

def test_edit_box_item(session, box_attributes, box_item_attributes):
    """Test editing an existing item in a box."""
    # Add a box first
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Add an item to the box
    item = BoxItem(box_id=box_model.id, **box_item_attributes)
    item.add_item(session)

    # Edit the item
    item.edit_item(session, item_location="Bottom Shelf", item_description="Updated Item Description")

    # Query to verify the item was edited
    edited_item = session.query(BoxItemModel).filter_by(item_description="Updated Item Description").first()

    assert edited_item is not None
    assert edited_item.item_location == "Bottom Shelf"
    assert edited_item.item_description == "Updated Item Description"

def test_delete_box_item(session, box_attributes, box_item_attributes):
    """Test deleting an item from a box in the database."""
    # Add a box first
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Add an item to the box
    item = BoxItem(box_id=box_model.id, **box_item_attributes)
    item.add_item(session)

    # Delete the item
    item.delete_item(session)

    # Query to verify the item was deleted
    deleted_item = session.query(BoxItemModel).filter_by(item_description="Test Item").first()

    assert deleted_item is None

def test_box_item_association(session, box_attributes, box_item_attributes):
    """Test the association between Box and BoxItem."""
    # Add a box
    box = Box(**box_attributes)
    box_model = box.add_box(session)

    # Add two items to the box
    item1 = BoxItem(box_id=box_model.id, item_height=2.5, item_length=3.0, item_weight=1.0, item_location="Top Shelf", item_description="Item 1")
    item2 = BoxItem(box_id=box_model.id, item_height=3.0, item_length=4.0, item_weight=2.0, item_location="Bottom Shelf", item_description="Item 2")

    item1.add_item(session)
    item2.add_item(session)

    # Verify that the box has two items
    box_with_items = session.query(BoxModel).filter_by(id=box_model.id).first()
    assert len(box_with_items.items) == 2
    assert box_with_items.items[0].item_description == "Item 1"
    assert box_with_items.items[1].item_description == "Item 2"
