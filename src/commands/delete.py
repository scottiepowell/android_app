import click
from src.box import Box
from src.boxitem import BoxItem
from src.database import SessionLocal

@click.group()
def delete():
    """Delete boxes and items."""
    pass

@delete.command()
@click.option('--box-id', type=int, required=True, help='ID of the box to delete.')
def box(box_id):
    """Delete a box."""
    session = SessionLocal()
    try:
        box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
        box.box_QRcode = None  # Assuming you can retrieve the QR code using box_id
        box.delete_box(session, box_id=box_id)
        click.echo(f'Deleted box with ID: {box_id}')
    finally:
        session.close()

# Similar command for deleting items
