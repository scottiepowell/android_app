from src.base import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

class BoxModel(Base):
    __tablename__ = 'boxes'

    id = Column(Integer, primary_key=True)
    alias = Column(String, unique=True, nullable=False)
    box_height = Column(Float, nullable=True)
    box_length = Column(Float, nullable=True)
    box_weight = Column(Float, nullable=True)
    box_location = Column(String, nullable=True)
    box_QRcode = Column(String, nullable=True, unique=True)
    box_picture = Column(LargeBinary)
    box_thumbnail = Column(LargeBinary)
    box_user_defined_tags = Column(String, nullable=True)
    box_description = Column(String, nullable=False)

    items = relationship("BoxItemModel", back_populates="box", cascade="all, delete-orphan")


class BoxItemModel(Base):
    __tablename__ = 'box_items'

    id = Column(Integer, primary_key=True)
    alias = Column(String, unique=True, nullable=False)
    box_id = Column(Integer, ForeignKey('boxes.id'), nullable=False)  # Foreign key to Box
    item_height = Column(Float, nullable=True)
    item_length = Column(Float, nullable=True)
    item_weight = Column(Float, nullable=True)
    item_location = Column(String, nullable=True)  # Location inside the box
    item_picture = Column(LargeBinary, nullable=True)
    item_thumbnail = Column(LargeBinary, nullable=True)
    item_user_defined_tags = Column(String, nullable=True)  # Tags as a comma-separated string
    item_description = Column(String, nullable=False)

    box = relationship("BoxModel", back_populates="items")
