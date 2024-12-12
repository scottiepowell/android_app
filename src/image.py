from PIL import Image
import io
import os
import logging

logger = logging.getLogger(__name__)


class ImageHandler:
    @staticmethod
    def load_image(file_path):
        """Load an image from a file and return it as binary data."""
        logger.debug(f"Attempting to load image from: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'rb') as f:
            image_data = f.read()
        logger.debug(f"Loaded image data size: {len(image_data)} bytes")
        return image_data

    @staticmethod
    def create_thumbnail(image_data, max_size=(100, 100)):
        """Create a thumbnail for the image."""
        logger.debug(f"Creating thumbnail for image of size: {len(image_data)} bytes")
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(max_size)
            output = io.BytesIO()
            image.save(output, format="JPEG")
            thumbnail_data = output.getvalue()
            logger.debug(f"Thumbnail created. Size: {len(thumbnail_data)} bytes")
            return thumbnail_data
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            raise

    @staticmethod
    def save_to_database(session, model, field, data):
        """Save image data to a database model."""
        if not isinstance(data, (bytes, type(None))):
            logger.error(f"Invalid data type for database field: {type(data)}. Expected bytes or None.")
            raise ValueError("Data must be bytes or None.")

        setattr(model, field, data)
        session.add(model)
        session.commit()
        logger.debug(f"Image data saved to field '{field}' in model ID {model.id}")

        # Verify the save
        result = session.query(model.__class__).filter_by(id=model.id).first()
        if result and getattr(result, field):
            logger.debug(f"Verified image saved. Field '{field}' size: {len(getattr(result, field))} bytes")
        else:
            logger.error(f"Image data not found in database field '{field}' for model ID {model.id}")