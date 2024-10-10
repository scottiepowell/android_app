import click
from src.box import Box
from src.boxitem import BoxItem
from src.database import SessionLocal

@click.group()
def edit():
    """Edit boxes and items."""
    pass

@edit.command()
@click.option('--box-id', type=int, required=True, help='ID of the box to edit.')
@click.option('--height', type=float, help='New height of the box.')
@click.option('--length', type=float, help='New length of the box.')
@click.option('--weight', type=float, help='New weight of the box.')
@click.option('--location', help='New location of the box.')
@click.option('--description', help='New description of the box.')
def box(box_id, height, length, weight, location, description):
    """Edit an existing box."""
    session = SessionLocal()
    try:
        kwargs = {k: v for k, v in [
            ('box_height', height),
            ('box_length', length),
            ('box_weight', weight),
            ('box_location', location),
            ('box_description', description)
        ] if v is not None}

        if kwargs:
            box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
            box.edit_box(session, box_id=box_id, **kwargs)
            click.echo(f'Box ID: {box_id} updated.')
        else:
            click.echo('No updates provided.')
    finally:
        session.close()

@edit.command()
@click.option('--item-id', type=int, required=True, help='ID of the item to edit.')
@click.option('--height', type=float, help='New height of the item.')
@click.option('--length', type=float, help='New length of the item.')
@click.option('--weight', type=float, help='New weight of the item.')
@click.option('--location', help='New location of the item.')
@click.option('--description', help='New description of the item.')
def item(item_id, height, length, weight, location, description):
    """Edit an existing item."""
    session = SessionLocal()
    try:
        # Build a dictionary of provided attributes to update
        kwargs = {k: v for k, v in [
            ('item_height', height),
            ('item_length', length),
            ('item_weight', weight),
            ('item_location', location),
            ('item_description', description)
        ] if v is not None}

        if kwargs:
            BoxItem.edit_item(session, item_id=item_id, **kwargs)
            click.echo(f'Item ID: {item_id} updated.')
        else:
            click.echo('No updates provided.')
    finally:
        session.close()