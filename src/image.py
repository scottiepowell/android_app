from PIL import Image, ExifTags
from pathlib import Path
import io
import os
import logging

from kivy.graphics.texture import Texture

logger = logging.getLogger(__name__)


class ImageHandler:
    @staticmethod
    def resolve_asset(relative_path):
        """Load an asset relative to the project's root directory and return its binary content."""
        try:
            # Determine the base path (project root)
            base_path = Path(__file__).resolve().parents[1]  # Navigate to the project root directory
            asset_path = base_path / relative_path

            # Log for debugging
            logger.debug(f"Resolving asset path: Base path: {base_path}, Asset path: {asset_path}")

            # Ensure the path exists
            if not asset_path.is_file():
                logger.error(f"Asset not found: {asset_path}")
                raise FileNotFoundError(f"Asset not found: {asset_path}")

            # Load and return the binary content of the file
            with asset_path.open("rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error resolving or loading asset: {e}")
            raise

    @staticmethod
    def load_image(file_path):
        """Load an image from a file, fix orientation, and return binary data."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'rb') as f:
            image_data = f.read()
        # Fix orientation
        image = Image.open(io.BytesIO(image_data))
        image = ImageHandler.fix_orientation(image)
        output = io.BytesIO()
        image.save(output, format="JPEG")
        return output.getvalue()

    @staticmethod
    def create_thumbnail(image_data, max_size=(100, 100)):
        """Create a thumbnail for the image."""
        image = Image.open(io.BytesIO(image_data))
        image = ImageHandler.fix_orientation(image)
        image.thumbnail(max_size)
        output = io.BytesIO()
        image.save(output, format="JPEG")
        return output.getvalue()

    @staticmethod
    def resize_default_thumbnail(default_image_data, size=(100, 100)):
        """Resize the default 'N/A' image to match the size of other thumbnails."""
        try:
            image = Image.open(io.BytesIO(default_image_data))
            image = image.resize(size, Image.Resampling.LANCZOS)
            output = io.BytesIO()
            image.save(output, format="JPEG")
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error resizing default thumbnail: {e}")
            raise

    @staticmethod
    def fix_orientation(image):
        """Fix image orientation using EXIF data."""
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # No EXIF data or orientation tag
            pass
        return image

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

    @staticmethod
    def bytes_to_texture(image_data):
        """Convert image bytes to Kivy Texture."""
        image = Image.open(io.BytesIO(image_data))
        image = image.convert("RGBA")
        data = image.tobytes()
        texture = Texture.create(size=image.size)
        texture.blit_buffer(data, colorfmt="rgba", bufferfmt="ubyte")
        texture.flip_vertical()  # Ensure correct orientation
        return texture