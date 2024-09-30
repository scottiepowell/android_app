from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Box(Base):
    __tablename__ = 'boxes'

    id = Column(Integer, primary_key=True)
    box_height = Column(Float, nullable=False)
    box_length = Column(Float, nullable=False)
    box_weight = Column(Float, nullable=False)
    box_location = Column(String, nullable=False)
    box_QRcode = Column(String, nullable=False, unique=True)
    box_picture = Column(String, nullable=True)
    box_user_defined_tags = Column(String, nullable=True)
    box_description = Column(String, nullable=True)

    items = relationship("BoxItem", back_populates="box")


class BoxItem(Base):
    __tablename__ = 'box_items'

    id = Column(Integer, primary_key=True)
    box_id = Column(Integer, ForeignKey('boxes.id'), nullable=False)  # Foreign key to Box
    item_height = Column(Float, nullable=False)
    item_length = Column(Float, nullable=False)
    item_weight = Column(Float, nullable=False)
    item_location = Column(String, nullable=False)  # Location inside the box
    item_picture = Column(String, nullable=True)  # Path to image file
    item_user_defined_tags = Column(String, nullable=True)  # Tags as a comma-separated string
    item_description = Column(String, nullable=True)

    box = relationship("Box", back_populates="items")
