import click
from src.box import Box
from src.boxitem import BoxItem
from src.database import SessionLocal

@click.group()
def add():
    """Add boxes and items."""
    pass

@add.command()
@click.option('--description', required=True, help='Description of the box.')
@click.option('--height', type=float, default=None, help='Height of the box.')
@click.option('--length', type=float, default=None, help='Length of the box.')
@click.option('--weight', type=float, default=None, help='Weight of the box.')
@click.option('--location', default=None, help='Location of the box.')
@click.option('--picture', default=None, help='Path to the box picture.')
@click.option('--tags', default=None, help='User-defined tags for the box, comma-separated.')
def box(description, height, length, weight, location, picture, tags):
    """Add a new box."""
    session = SessionLocal()
    try:
        box = Box(
            box_description=description,
            box_height=height,
            box_length=length,
            box_weight=weight,
            box_location=location,
            box_user_defined_tags=tags
        )
        box_model = box.add_box(session)

        if picture:
            box.add_picture(session, box_model.id, picture)

        click.echo(f'Added box with ID: {box_model.id}')
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        session.close()

@add.command()
@click.option('--box-id', type=int, required=True, help='ID of the box to add the item to.')
@click.option('--height', type=float, required=None, help='Height of the item.')
@click.option('--length', type=float, default=None, help='Length of the item.')
@click.option('--weight', type=float, default=None, help='Weight of the item.')
@click.option('--location', default=None, help='Location of the item.')
@click.option('--description', required=True, help='Description of the item.')
@click.option('--picture', default=None, help='Path to the item picture.')
@click.option('--tags', default=None, help='User-defined tags for the item, comma-separated.')
def item(box_id, description, location, height, length, weight, picture, tags):
    """Add a new item to a box."""
    session = SessionLocal()
    try:
        box_item = BoxItem(
            box_id=box_id,
            item_height=height,
            item_length=length,
            item_weight=weight,
            item_location=location,
            item_description=description,
            item_user_defined_tags=tags
        )
        item_model = box_item.add_item(session)

        if picture:
            box_item.add_picture(session, picture)

        click.echo(f'Added item with ID: {item_model.id} to box ID: {box_id}')
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        session.close()
