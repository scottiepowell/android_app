# box.py
import random
import string
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.base import Base

#Base = declarative_base()

class Box(Base):
    __tablename__ = 'boxes'

    id = Column(Integer, primary_key=True)
    box_height = Column(Float, nullable=False)
    box_length = Column(Float, nullable=False)
    box_weight = Column(Float, nullable=False)
    box_location = Column(String, nullable=False)  # Address as a string for now
    box_QRcode = Column(String, nullable=False, unique=True)  # Placeholder for QR code
    box_picture = Column(String, nullable=True)  # Path to image file
    box_user_defined_tags = Column(String, nullable=True)  # Tags as a comma-separated string
    box_description = Column(String, nullable=True)

    items = relationship("BoxItem", back_populates="box") # One-to-many relationship with BoxItem

    def __init__(self, **kwargs):
        """Initialize a Box instance and generate a random QR code if not provided."""
        super().__init__(**kwargs)
        if not self.box_QRcode:
            self.box_QRcode = self.generate_random_qrcode()

    @staticmethod
    def generate_random_qrcode(length=10):
        """Generate a random QR code consisting of uppercase letters and digits."""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def add_box(self, session):
        """Add this box to the database."""
        session.add(self)
        session.commit()

    def edit_box(self, session, **kwargs):
        """Edit box attributes with provided keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.commit()

    def delete_box(self, session):
        """Delete this box from the database."""
        session.delete(self)
        session.commit()