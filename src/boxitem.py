# boxitem.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.base import Base

class BoxItem(Base):
    __tablename__ = 'box_items'

    id = Column(Integer, primary_key=True)
    box_id = Column(Integer, ForeignKey('boxes.id'))  # Foreign key to Box
    item_height = Column(Float, nullable=False)
    item_length = Column(Float, nullable=False)
    item_weight = Column(Float, nullable=False)
    item_location = Column(String, nullable=False)  # Location inside the box
    item_picture = Column(String, nullable=True)  # Path to image file
    item_user_defined_tags = Column(String, nullable=True)  # Tags as a comma-separated string
    item_description = Column(String, nullable=True)

    box = relationship("Box", back_populates="items")

    def add_item(self, session):
        """Add this item to the box"""
        session.add(self)
        session.commit()

    def edit_item(self, session, **kwargs):
        """Edit item attributes with provided keyword arguments"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.commit()

    def delete_item(self, session):
        """Delete this item from the box"""
        session.delete(self)
        session.commit()