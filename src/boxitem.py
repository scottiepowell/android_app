from src.models import BoxItemModel as BoxItemModel
from sqlalchemy.orm import Session

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
        self.item_id = item_id  # Track the ID for updates and deletions

    def to_model(self):
        """Convert the business logic object to the database model for saving."""
        return BoxItemModel(
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
        """Add this item to the box in the database."""
        item_model = self.to_model()
        session.add(item_model)
        session.commit()
        self.item_id = item_model.id  # Save the ID for future edits or deletions
        return item_model

    def edit_item(self, session: Session, **kwargs):
        """Edit an existing item in the database."""
        if not self.item_id:
            raise ValueError("BoxItem ID is not set.")

        # Query by the item's primary key ID, not box_id
        item_model = session.query(BoxItemModel).filter_by(id=self.item_id).first()
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