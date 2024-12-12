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
@click.option('--picture', default=None, help='Path to new box picture, or "none" to remove existing picture.')
def box(box_id, height, length, weight, location, description, picture):
    """Edit an existing box."""
    session = SessionLocal()
    try:
        box_obj = Box(box_height=None, box_length=None, box_weight=None, box_location=None)

        kwargs = {k: v for k, v in [
            ('box_height', height),
            ('box_length', length),
            ('box_weight', weight),
            ('box_location', location),
            ('box_description', description)
        ] if v is not None}

        if kwargs:
            box_obj.edit_box(session, box_id=box_id, **kwargs)
            click.echo(f'Box ID: {box_id} updated.')
        else:
            click.echo('No updates provided.')

        if picture is not None:
            if picture.lower() == "none":
                # Remove picture
                box_obj.remove_picture(session, box_id)
                click.echo(f'Removed picture from Box ID: {box_id}')
            else:
                # Update picture
                box_obj.add_picture(session, box_id, picture)
                click.echo(f'Updated picture for Box ID: {box_id}')

    except Exception as e:
            click.echo(f"Error editing box: {e}")
    finally:
        session.close()

@edit.command()
@click.option('--item-id', type=int, required=True, help='ID of the item to edit.')
@click.option('--height', type=float, help='New height of the item.')
@click.option('--length', type=float, help='New length of the item.')
@click.option('--weight', type=float, help='New weight of the item.')
@click.option('--location', help='New location of the item.')
@click.option('--description', help='New description of the item.')
@click.option('--picture', default=None, help='Path to new item picture, or "none" to remove existing picture.')
def item(item_id, height, length, weight, location, description, picture):
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

        if picture is not None:
            box_item = BoxItem(
                box_id=None,  # Not needed for updating picture
                item_height=None,
                item_length=None,
                item_weight=None,
                item_location=None
            )
            box_item.item_id = item_id  # Set the item ID explicitly

            if picture.lower() == "none":
                # Remove picture
                box_item.add_picture(session, None)
                click.echo(f'Removed picture from Item ID: {item_id}')
            else:
                # Update picture
                box_item.add_picture(session, picture)
                click.echo(f'Updated picture for Item ID: {item_id}')

    except Exception as e:
        click.echo(f"Error editing item: {e}")
    finally:
        session.close()