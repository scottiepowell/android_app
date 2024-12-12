import random
import logging
from src.models import BoxItemModel as BoxItemModel
from src.image import ImageHandler
from sqlalchemy.orm import Session
from src.utils.alias_utils import load_aliases, generate_unique_alias, find_theme_for_box

logger = logging.getLogger(__name__)

class BoxItem:
    def __init__(self, box_id, item_height, item_length, item_weight, item_location, item_description=None,
                 item_picture=None, item_user_defined_tags=None, item_id=None):
        """Initialize a BoxItem instance with business logic."""
        self.box_id = box_id
        self.item_height = item_height
        self.item_length = item_length
        self.item_weight = item_weight
        self.item_location = item_location
        self.item_description = item_description
        self.item_picture = item_picture
        self.item_user_defined_tags = item_user_defined_tags
        self.item_id = item_id
        self.alias = None

    def to_model(self):
        """Convert the business logic object to the database model for saving."""
        print(f"BoxItem to_model called with box_id: {self.box_id}")
        return BoxItemModel(
            alias=self.alias,
            box_id=self.box_id,
            item_height=self.item_height,
            item_length=self.item_length,
            item_weight=self.item_weight,
            item_location=self.item_location,
            item_description=self.item_description,
            item_picture=self.item_picture,
            item_user_defined_tags=self.item_user_defined_tags
        )

    @staticmethod
    def find_boxitem(session: Session, item_location="Top Shelf", item_weight=None):
        """Find box items by location or weight."""
        query = session.query(BoxItemModel).filter(BoxItemModel.item_location.ilike(f"%{item_location}%"))
        if item_weight:
            query = query.filter(BoxItemModel.item_weight == item_weight)
        return query.all()

    def add_item(self, session: Session):
        try:
            alias_dict = load_aliases()

            # Determine the theme based on the box
            theme = find_theme_for_box(session, self.box_id, alias_dict)

            # Generate a unique alias for the box item
            self.alias = generate_unique_alias(session, BoxItemModel, theme, alias_dict)

            # Add this item to the box in the database
            item_model = self.to_model()
            session.add(item_model)
            session.commit()

            session.refresh(item_model) # refresh the instance to the id
            self.item_id = item_model.id # set the ide after getting it back

            logger.debug(f"Item added with ID: {self.item_id}, alias: {self.alias}")
            return item_model
        except Exception as e:
            session.rollback()
            print(f"Error adding item: {e}")
            raise

    def add_picture(self, session: Session, picture_path: str):
        """Add or update a picture for the box item."""
        logger.debug(f"Adding picture for box item ID: {self.item_id} from file: {picture_path}")

        # Load the image and create a thumbnail
        try:
            image_data = ImageHandler.load_image(picture_path)
            thumbnail = ImageHandler.create_thumbnail(image_data)
        except Exception as e:
            logger.error(f"Error loading or processing image: {e}")
            raise

        # Retrieve the box item model and update its picture fields
        model = session.query(BoxItemModel).filter_by(id=self.item_id).first()
        if not model:
            logger.error(f"BoxItem with ID {self.item_id} not found in the database.")
            raise ValueError(f"BoxItem with ID {self.item_id} not found.")

        try:
            ImageHandler.save_to_database(session, model, 'item_picture', image_data)
            ImageHandler.save_to_database(session, model, 'item_thumbnail', thumbnail)
        except Exception as e:
            logger.error(f"Error saving image to database: {e}")
            raise

        logger.debug(f"Picture added for box item ID: {self.item_id}")

    @classmethod
    def edit_item(cls, session: Session, item_id: int, **kwargs):
        """Edit an existing item in the database."""
        # Query by the item's primary key ID, not box_id
        item_model = session.query(BoxItemModel).filter_by(id=item_id).first()
        if not item_model:
            raise ValueError("BoxItem not found.")

        # Update attributes
        for key, value in kwargs.items():
            if hasattr(item_model, key):
                setattr(item_model, key, value)
        session.commit()

    def delete_item(self, session: Session):
        """Delete the item from the box in the database."""
        if not self.item_id:
            raise ValueError("BoxItem ID is not set.")

        # Query by the item's primary key ID, not box_id
        item_model = session.query(BoxItemModel).filter_by(id=self.item_id).first()
        if not item_model:
            raise ValueError("BoxItem not found.")
        session.delete(item_model)
        session.commit()

    def remove_picture(self, session: Session):
        """Remove the picture and thumbnail from the box item."""
        logger.debug(f"Removing picture for box item ID: {self.item_id}")

        # Retrieve the box item model
        model = session.query(BoxItemModel).filter_by(id=self.item_id).first()
        if not model:
            logger.error(f"BoxItem with ID {self.item_id} not found in the database.")
            raise ValueError(f"BoxItem with ID {self.item_id} not found.")

        # Set picture and thumbnail fields to None
        model.item_picture = None
        model.item_thumbnail = None
        session.commit()

        logger.debug(f"Picture removed for box item ID: {self.item_id}")