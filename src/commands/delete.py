import click
from src.box import Box
from src.boxitem import BoxItem
from src.database import SessionLocal

@click.group()
def delete():
    """Delete boxes, items, or associated data."""
    pass

@delete.command()
@click.option('--box-id', type=int, required=True, help='ID of the box to delete.')
def box(box_id):
    """Delete a box from the database."""
    session = SessionLocal()
    try:
        box_obj = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
        # If your delete_box method requires a box_id, you may need to pass it:
        # Adjust as needed if your delete_box method signature is different.
        box_obj.delete_box(session, box_id=box_id)
        click.echo(f'Deleted box with ID: {box_id}')
    except Exception as e:
        click.echo(f"Error deleting box: {e}")
    finally:
        session.close()

@delete.command('box-picture')
@click.option('--box-id', type=int, required=True, help='ID of the box from which to remove the picture.')
def box_picture(box_id):
    """Remove only the box picture and thumbnail, but keep the box record intact."""
    session = SessionLocal()
    try:
        box_obj = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
        # Call the remove_picture method which sets box_picture and box_thumbnail to None
        box_obj.remove_picture(session, box_id)
        click.echo(f'Removed picture from box with ID: {box_id}')
    except Exception as e:
        click.echo(f"Error removing box picture: {e}")
    finally:
        session.close()

@delete.command('item-picture')
@click.option('--item-id', type=int, required=True, help='ID of the item from which to remove the picture.')
def item_picture(item_id):
    """Remove the picture and thumbnail from a box item, but keep the item record intact."""
    session = SessionLocal()
    try:
        # Initialize the BoxItem object
        box_item = BoxItem(
            box_id=None,  # Not needed for picture removal
            item_height=None,
            item_length=None,
            item_weight=None,
            item_location=None
        )
        box_item.item_id = item_id  # Set the item ID explicitly

        # Remove the picture
        box_item.remove_picture(session)  # Passing None removes the picture
        click.echo(f'Removed picture from item with ID: {item_id}')
    except Exception as e:
        click.echo(f"Error removing item picture: {e}")
    finally:
        session.close()