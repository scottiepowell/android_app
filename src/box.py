# src/box.py
import string
import random
import logging
from src.models import BoxModel
from sqlalchemy.orm import Session
from src.image import ImageHandler
from src.utils.alias_utils import load_aliases, generate_unique_alias

logger = logging.getLogger(__name__)

class Box:
    def __init__(self, box_height, box_length, box_weight, box_location, box_description=None,
                 box_user_defined_tags=None, box_QRcode=None):
        """Initialize a Box instance with business logic."""
        self.box_height = box_height
        self.box_length = box_length
        self.box_weight = box_weight
        self.box_location = box_location
        self.box_picture = None
        self.box_description = box_description or "this is a box"
        self.box_user_defined_tags = box_user_defined_tags
        self.box_QRcode = box_QRcode or self.generate_random_qrcode()
        self.alias = None

    @staticmethod
    def generate_random_qrcode(length=10):
        """Generate a random QR code consisting of uppercase letters and digits."""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def find_box(session: Session, box_location=None, box_weight=None):
        """Find boxes by location or weight."""
        query = session.query(BoxModel)

        if box_location:
            query = query.filter(BoxModel.box_location.ilike(f"%{box_location}%"))
        if box_weight:
            query = query.filter(BoxModel.box_weight == box_weight)

        return query.all()

    def to_model(self):
        """Convert the business logic object to the database model for saving."""
        return BoxModel(
            alias=self.alias,
            box_height=self.box_height,
            box_length=self.box_length,
            box_weight=self.box_weight,
            box_location=self.box_location,
            box_description=self.box_description,
            box_picture=None,
            box_user_defined_tags=self.box_user_defined_tags,
            box_QRcode=self.box_QRcode
        )

    def add_box(self, session: Session, theme="animals"):
        """Add this box to the database with a unique alias."""

        alias_dict = load_aliases()
        if theme not in alias_dict:
            raise ValueError(f"Theme '{theme}' not found in aliases.")

        self.alias = generate_unique_alias(session, BoxModel, theme, alias_dict, is_box=True)

        box_model = self.to_model()
        session.add(box_model)
        session.commit()
        return box_model

    def edit_box(self, session: Session, box_id: int, **kwargs):
        """Edit an existing box in the database."""
        box_model = session.query(BoxModel).filter_by(id=box_id).first()

        if not box_model:
            raise ValueError("Box not found.")

        # Update attributes
        for key, value in kwargs.items():
            if hasattr(box_model, key):
                setattr(box_model, key, value)
        session.commit()

    def delete_box(self, session: Session):
        """Delete the box from the database."""
        box_model = session.query(BoxModel).filter_by(box_QRcode=self.box_QRcode).first()
        if not box_model:
            raise ValueError("Box not found.")
        session.delete(box_model)
        session.commit()

    def add_picture(self, session, box_id, picture_path):
        """Add or update a picture for the box."""
        logger.debug(f"Adding picture for box ID: {box_id} from file: {picture_path}")

        # Load the image and create a thumbnail
        try:
            image_data = ImageHandler.load_image(picture_path)
            thumbnail = ImageHandler.create_thumbnail(image_data)
        except Exception as e:
            logger.error(f"Error loading or processing image: {e}")
            raise

        # Retrieve the box model and update its picture fields
        model = session.query(BoxModel).filter_by(id=box_id).first()
        if not model:
            logger.error(f"Box with ID {box_id} not found in the database.")
            raise ValueError(f"Box with ID {box_id} not found.")

        try:
            ImageHandler.save_to_database(session, model, 'box_picture', image_data)
            ImageHandler.save_to_database(session, model, 'box_thumbnail', thumbnail)
        except Exception as e:
            logger.error(f"Error saving image to database: {e}")
            raise
        logger.debug(f"Verifying image data for box ID: {box_id}")
        saved_box = session.query(BoxModel).filter_by(id=box_id).first()
        if saved_box:
            logger.debug(f"box_picture size: {len(saved_box.box_picture) if saved_box.box_picture else 'NULL'}")
            logger.debug(f"box_thumbnail size: {len(saved_box.box_thumbnail) if saved_box.box_thumbnail else 'NULL'}")
        else:
            logger.error(f"Box with ID {box_id} not found after save.")

    def remove_picture(self, session: Session, box_id: int):
        """Remove the picture and thumbnail from the box."""
        model = session.query(BoxModel).filter_by(id=box_id).first()
        if not model:
            raise ValueError(f"Box with ID {box_id} not found.")
        model.box_picture = None
        model.box_thumbnail = None
        session.commit()