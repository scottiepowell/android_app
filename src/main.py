# main.py
import logging
from install_or_update_packages import install_or_update_packages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.box import Box
from src.boxitem import BoxItem
from src.base import Base

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_session():
    """Create a new database session."""
    engine = create_engine('sqlite:///whats_in_the_box.db')  # Using SQLite for local testing
    Base.metadata.create_all(engine)  # Create tables if they don't exist
    Session: sessionmaker[Session] = sessionmaker(bind=engine)
    return Session()

def verify_add_box():
    """Verify that the add_box method works."""
    session = create_session()

    # Create a new Box instance
    new_box = Box(
        box_height=12.5,
        box_length=10.0,
        box_weight=5.5,
        box_location="Warehouse A",
        box_QRcode="123456789",
        box_picture="/path/to/image.jpg",
        box_user_defined_tags="fragile,priority",
        box_description="A sample box"
    )

    # Add the box to the database using add_box()
    new_box.add_box(session)

    # Query the database to verify the box was added
    added_box = session.query(Box).filter_by(box_QRcode="123456789").first()

    if added_box:
        print(f"Box added successfully: {added_box.box_location}, {added_box.box_description}")
    else:
        print("Failed to add box.")

def verify_edit_box():
    """Verify that the edit_box method works."""
    session = create_session()

    # Fetch the box to edit
    box_to_edit = session.query(Box).filter_by(box_QRcode="123456789").first()

    if box_to_edit:
        # Edit the box details
        box_to_edit.edit_box(session, box_location="Warehouse B", box_description="Updated description")

        # Query the database to verify the edit
        edited_box = session.query(Box).filter_by(box_QRcode="123456789").first()

        if edited_box.box_location == "Warehouse B" and edited_box.box_description == "Updated description":
            print(f"Box edited successfully: {edited_box.box_location}, {edited_box.box_description}")
        else:
            print("Failed to edit box.")
    else:
        print("Box not found for editing.")


def verify_delete_box():
    """Verify that the delete_box method works with detailed logging."""
    session = create_session()

    try:
        # Log all existing boxes before deletion for better visibility
        existing_boxes = session.query(Box).all()
        for box in existing_boxes:
            logger.debug(
                f"Existing box before deletion: ID={box.id}, QRcode={box.box_QRcode}, Location={box.box_location}")

        # Fetch the box to delete
        logger.debug("Querying for box with QR code 123456789 to delete.")
        box_to_delete = session.query(Box).filter_by(box_QRcode="123456789").first()

        if box_to_delete:
            logger.debug(
                f"Box found: ID={box_to_delete.id}, Location={box_to_delete.box_location}, Description={box_to_delete.box_description}")

            # Delete the box
            logger.debug(f"Attempting to delete box ID={box_to_delete.id}.")
            box_to_delete.delete_box(session)

            # Commit changes and check for deletion
            session.commit()
            logger.debug("Delete committed to database.")

            # Log all existing boxes after deletion for better visibility
            existing_boxes_after_delete = session.query(Box).all()
            for box in existing_boxes_after_delete:
                logger.debug(
                    f"Existing box after deletion attempt: ID={box.id}, QRcode={box.box_QRcode}, Location={box.box_location}")

            # Verify deletion by querying the specific ID again
            session.expire_all()  # Clear session cache
            logger.debug(f"Querying again to verify deletion of box ID={box_to_delete.id}.")
            deleted_box = session.query(Box).filter_by(id=box_to_delete.id).first()

            if not deleted_box:
                logger.info("Box deleted successfully.")
            else:
                logger.error(
                    f"Failed to delete box. Box still exists: ID={deleted_box.id}, Location={deleted_box.box_location}, Description={deleted_box.box_description}")
        else:
            logger.warning("Box not found for deletion.")

    except Exception as e:
        logger.error(f"An error occurred during deletion: {e}")
        session.rollback()  # Rollback in case of failure
    finally:
        session.close()  # Ensure session is closed

def verify_add_box_item():
    """Verify that the add_item method works for BoxItem."""
    session = create_session()

    # Fetch the box to add the item to
    box = session.query(Box).filter_by(box_QRcode="123456789").first()

    if box:
        # Create a new BoxItem instance
        new_item = BoxItem(
            box_id=box.id,
            item_height=2.5,
            item_length=4.0,
            item_weight=1.2,
            item_location="Top Shelf",
            item_picture="/path/to/item_image.jpg",
            item_user_defined_tags="fragile,electronics",
            item_description="A sample item"
        )

        # Add the item to the database using add_item()
        new_item.add_item(session)

        # Query the database to verify the item was added
        added_item = session.query(BoxItem).filter_by(item_description="A sample item").first()

        if added_item:
            print(f"Item added successfully: {added_item.item_location}, {added_item.item_description}")
        else:
            print("Failed to add item.")
    else:
        print("Box not found to add the item.")


def verify_edit_box_item():
    """Verify that the edit_item method works for BoxItem."""
    session = create_session()

    # Fetch the item to edit
    item_to_edit = session.query(BoxItem).filter_by(item_description="A sample item").first()

    if item_to_edit:
        # Edit the item details
        item_to_edit.edit_item(session, item_location="Bottom Shelf", item_description="Updated item description")

        # Query the database to verify the edit
        edited_item = session.query(BoxItem).filter_by(id=item_to_edit.id).first()

        if edited_item.item_location == "Bottom Shelf" and edited_item.item_description == "Updated item description":
            print(f"Item edited successfully: {edited_item.item_location}, {edited_item.item_description}")
        else:
            print("Failed to edit item.")
    else:
        print("Item not found for editing.")


def verify_delete_box_item():
    """Verify that the delete_item method works for BoxItem."""
    session = create_session()

    # Fetch the item to delete
    item_to_delete = session.query(BoxItem).filter_by(item_description="Updated item description").first()

    if item_to_delete:
        print(f"Deleting item: {item_to_delete.item_location}, {item_to_delete.item_description}")
        # Delete the item
        item_to_delete.delete_item(session)

        # Commit changes and check for deletion
        session.commit()

        # Verify deletion by querying the database again
        deleted_item = session.query(BoxItem).filter_by(id=item_to_delete.id).first()

        if not deleted_item:
            print("Item deleted successfully.")
        else:
            print("Failed to delete item.")
    else:
        print("Item not found for deletion.")


def main():
    # Call the function to install or update the packages
    print("Starting the package installation or update process...")
    install_or_update_packages()
    print("Package installation or update completed.")

    # Verify the Box operations
    verify_add_box()
    verify_edit_box()
    verify_delete_box()

    # Verify the BoxItem operations
    verify_add_box_item()
    verify_edit_box_item()
    verify_delete_box_item()


if __name__ == "__main__":
    main()
