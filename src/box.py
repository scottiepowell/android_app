# box.py
import random
import string
import random
from models import Box as BoxModel
from sqlalchemy.orm import Session


class Box:
    def __init__(self, box_height, box_length, box_weight, box_location, box_description=None, box_picture=None,
                 box_user_defined_tags=None, box_QRcode=None):
        """Initialize a Box instance with business logic."""
        self.box_height = box_height
        self.box_length = box_length
        self.box_weight = box_weight
        self.box_location = box_location
        self.box_description = box_description
        self.box_picture = box_picture
        self.box_user_defined_tags = box_user_defined_tags
        self.box_QRcode = box_QRcode or self.generate_random_qrcode()

    @staticmethod
    def generate_random_qrcode(length=10):
        """Generate a random QR code consisting of uppercase letters and digits."""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def to_model(self):
        """Convert the business logic object to the database model for saving."""
        return BoxModel(
            box_height=self.box_height,
            box_length=self.box_length,
            box_weight=self.box_weight,
            box_location=self.box_location,
            box_description=self.box_description,
            box_picture=self.box_picture,
            box_user_defined_tags=self.box_user_defined_tags,
            box_QRcode=self.box_QRcode
        )

    def add_box(self, session: Session):
        """Add this box to the database using the ORM model."""
        box_model = self.to_model()
        session.add(box_model)
        session.commit()
        return box_model

    def edit_box(self, session: Session, **kwargs):
        """Edit an existing box in the database."""
        box_model = session.query(BoxModel).filter_by(box_QRcode=self.box_QRcode).first()
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