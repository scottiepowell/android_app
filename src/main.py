# main.py
import logging
from install_or_update_packages import install_or_update_packages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from boxitem import BoxItem
from models import Base, Box, BoxItem as BoxItemModel
from box import Box, BoxModel

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_session():
    """Create a new database session."""
    engine = create_engine('sqlite:///whats_in_the_box.db')  # Using SQLite for local testing
    Base.metadata.create_all(engine)  # Create tables if they don't exist
    Session = sessionmaker(bind=engine)
    return Session()

def verify_add_box():
    """Verify that the add_box method works."""
    session = create_session()

    # Create a new Box instance using the business logic class
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

    # Add the box to the database using the business logic class
    new_box.add_box(session)

    # Query the database using the ORM model class to verify the box was added
    added_box = session.query(BoxModel).filter_by(box_QRcode="123456789").first()

    if added_box:
        print(f"Box added successfully: {added_box.box_location}, {added_box.box_description}")
    else:
        print("Failed to add box.")

    session.close()

def verify_edit_box():
    """Verify that the edit_box method works."""
    session = create_session()

    # Query for the box to edit using the ORM model
    box_model = session.query(BoxModel).filter_by(box_QRcode="123456789").first()

    if box_model:
        # Create a business logic Box instance to apply edits
        box_to_edit = Box(
            box_height=box_model.box_height,
            box_length=box_model.box_length,
            box_weight=box_model.box_weight,
            box_location=box_model.box_location,
            box_description=box_model.box_description,
            box_picture=box_model.box_picture,
            box_user_defined_tags=box_model.box_user_defined_tags,
            box_QRcode=box_model.box_QRcode
        )

        # Edit the box using the business logic class
        box_to_edit.edit_box(session, box_location="Warehouse B", box_description="Updated description")

        # Query the database to verify the edit
        edited_box = session.query(BoxModel).filter_by(box_QRcode="123456789").first()

        if edited_box.box_location == "Warehouse B" and edited_box.box_description == "Updated description":
            print(f"Box edited successfully: {edited_box.box_location}, {edited_box.box_description}")
        else:
            print("Failed to edit box.")
    else:
        print("Box not found for editing.")

    session.close()

def verify_delete_box():
    """Verify that the delete_box method works with detailed logging."""
    session = create_session()

    try:
        # Log all existing boxes before deletion for better visibility
        existing_boxes = session.query(BoxModel).all()
        for box in existing_boxes:
            logger.debug(f"Existing box before deletion: ID={box.id}, QRcode={box.box_QRcode}, Location={box.box_location}")

        # Query the box to delete using the ORM model
        logger.debug("Querying for box with QR code 123456789 to delete.")
        box_model = session.query(BoxModel).filter_by(box_QRcode="123456789").first()

        if box_model:
            # Create a business logic Box instance to handle the deletion
            box_to_delete = Box(
                box_height=box_model.box_height,
                box_length=box_model.box_length,
                box_weight=box_model.box_weight,
                box_location=box_model.box_location,
                box_description=box_model.box_description,
                box_picture=box_model.box_picture,
                box_user_defined_tags=box_model.box_user_defined_tags,
                box_QRcode=box_model.box_QRcode
            )

            logger.debug(f"Box found: ID={box_model.id}, Location={box_model.box_location}, Description={box_model.box_description}")

            # Delete the box using the business logic class
            logger.debug(f"Attempting to delete box ID={box_model.id}.")
            box_to_delete.delete_box(session)

            # Commit changes and check for deletion
            session.commit()
            logger.debug("Delete committed to database.")

            # Log all existing boxes after deletion for better visibility
            existing_boxes_after_delete = session.query(BoxModel).all()
            for box in existing_boxes_after_delete:
                logger.debug(f"Existing box after deletion attempt: ID={box.id}, QRcode={box.box_QRcode}, Location={box.box_location}")

            # Verify deletion by querying the specific ID again
            session.expire_all()  # Clear session cache
            logger.debug(f"Querying again to verify deletion of box ID={box_model.id}.")
            deleted_box = session.query(BoxModel).filter_by(id=box_model.id).first()

            if not deleted_box:
                logger.info("Box deleted successfully.")
            else:
                logger.error(f"Failed to delete box. Box still exists: ID={deleted_box.id}, Location={deleted_box.box_location}, Description={deleted_box.box_description}")
        else:
            logger.warning("Box not found for deletion.")

    except Exception as e:
        logger.error(f"An error occurred during deletion: {e}")
        session.rollback()  # Rollback in case of failure
    finally:
        session.close()  # Ensure session is closed

# BoxItem verification functions
def verify_add_box_item():
    """Verify that the add_item method works for BoxItem."""
    session = create_session()

    # Create a new Box instance to hold items
    new_box = Box(
        box_height=12.5,
        box_length=10.0,
        box_weight=5.5,
        box_location="Warehouse A",
        box_QRcode="BOX12345",
        box_picture="/path/to/image.jpg",
        box_user_defined_tags="fragile,priority",
        box_description="A sample box"
    )
    new_box.add_box(session)

    # Create a new BoxItem instance
    new_box_item = BoxItem(
        box_id=new_box.to_model().id,  # Linking the item to the new box
        item_height=2.0,
        item_length=1.5,
        item_weight=0.5,
        item_location="Top-left corner",
        item_description="A sample item",
        item_picture="/path/to/item_image.jpg",
        item_user_defined_tags="electronics"
    )

    # Add the item to the database using the business logic class
    new_box_item.add_item(session)

    # Query the database using the ORM model class to verify the item was added
    added_item = session.query(BoxItemModel).filter_by(item_description="A sample item").first()

    if added_item:
        print(f"Box item added successfully: {added_item.item_location}, {added_item.item_description}")
    else:
        print("Failed to add box item.")

    session.close()

def verify_edit_box_item():
    """Verify that the edit_item method works for BoxItem."""
    session = create_session()

    # Query for the box item to edit using the ORM model
    box_item_model = session.query(BoxItemModel).filter_by(item_description="A sample item").first()

    if box_item_model:
        # Create a business logic BoxItem instance to apply edits, passing in the item_id
        box_item_to_edit = BoxItem(
            box_id=box_item_model.box_id,
            item_height=box_item_model.item_height,
            item_length=box_item_model.item_length,
            item_weight=box_item_model.item_weight,
            item_location=box_item_model.item_location,
            item_description=box_item_model.item_description,
            item_picture=box_item_model.item_picture,
            item_user_defined_tags=box_item_model.item_user_defined_tags,
            item_id=box_item_model.id  # Pass the item_id for editing
        )

        # Edit the box item using the business logic class
        box_item_to_edit.edit_item(session, item_location="Bottom-right corner", item_description="Updated item")

        # Query the database to verify the edit
        edited_item = session.query(BoxItemModel).filter_by(id=box_item_model.id).first()

        if edited_item.item_location == "Bottom-right corner" and edited_item.item_description == "Updated item":
            print(f"Box item edited successfully: {edited_item.item_location}, {edited_item.item_description}")
        else:
            print("Failed to edit box item.")
    else:
        print("Box item not found for editing.")

    session.close()

def verify_delete_box_item():
    """Verify that the delete_item method works for BoxItem."""
    session = create_session()

    try:
        # Log all existing items before deletion for better visibility
        existing_items = session.query(BoxItemModel).all()
        for item in existing_items:
            logger.debug(f"Existing item before deletion: ID={item.id}, Description={item.item_description}, Location={item.item_location}")

        # Query the box item to delete using the ORM model
        box_item_model = session.query(BoxItemModel).filter_by(item_description="Updated item").first()

        if box_item_model:
            # Create a business logic BoxItem instance to handle the deletion
            box_item_to_delete = BoxItem(
                box_id=box_item_model.box_id,
                item_height=box_item_model.item_height,
                item_length=box_item_model.item_length,
                item_weight=box_item_model.item_weight,
                item_location=box_item_model.item_location,
                item_description=box_item_model.item_description,
                item_picture=box_item_model.item_picture,
                item_user_defined_tags=box_item_model.item_user_defined_tags,
                item_id = box_item_model.id
            )

            logger.debug(f"Item found: ID={box_item_model.id}, Description={box_item_model.item_description}, Location={box_item_model.item_location}")

            # Delete the box item using the business logic class
            logger.debug(f"Attempting to delete item ID={box_item_model.id}.")
            box_item_to_delete.delete_item(session)

            # Commit changes and check for deletion
            session.commit()
            logger.debug("Delete committed to database.")

            # Log all existing items after deletion for better visibility
            existing_items_after_delete = session.query(BoxItemModel).all()
            for item in existing_items_after_delete:
                logger.debug(f"Existing item after deletion attempt: ID={item.id}, Description={item.item_description}, Location={item.item_location}")

            # Verify deletion by querying the specific ID again
            session.expire_all()  # Clear session cache
            logger.debug(f"Querying again to verify deletion of item ID={box_item_model.id}.")
            deleted_item = session.query(BoxItemModel).filter_by(id=box_item_model.id).first()

            if not deleted_item:
                logger.info("Box item deleted successfully.")
            else:
                logger.error(f"Failed to delete box item. Item still exists: ID={deleted_item.id}, Description={deleted_item.item_description}, Location={deleted_item.item_location}")
        else:
            logger.warning("Box item not found for deletion.")

    except Exception as e:
        logger.error(f"An error occurred during deletion: {e}")
        session.rollback()  # Rollback in case of failure
    finally:
        session.close()  # Ensure session is closed

def main():
    # Call the function to install or update the packages
    #print("Starting the package installation or update process...")
    #install_or_update_packages()
    #print("Package installation or update completed.")

    # Verify the Box operations
    verify_add_box()
    verify_edit_box()
    verify_delete_box()

    # verify the BoxItem operations
    verify_add_box_item()
    verify_edit_box_item()
    verify_delete_box_item()

if __name__ == "__main__":
    main()
