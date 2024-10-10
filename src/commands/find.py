#src/commands/find.py
import click
from tabulate import tabulate
from src.box import Box
from src.boxitem import BoxItem
from src.database import SessionLocal
from src.models import BoxModel, BoxItemModel

@click.group()
def find():
    """Find boxes and items."""
    pass

@find.command()
@click.option('--location', default='', help='Location to search for boxes.')
@click.option('--weight', type=float, help='Weight to search for boxes.')
def boxes(location, weight):
    """Find boxes based on criteria."""
    session = SessionLocal()
    try:
        results = Box.find_box(session, box_location=location if location else None, box_weight=weight)
        if results:
            for box in results:
                click.echo(f'Box ID: {box.id}, Location: {box.box_location}, Weight: {box.box_weight}')
        else:
            click.echo('No boxes found.')
    finally:
        session.close()

@find.command()
def all():
    """Find all boxes and their items, sorted by box ID (low to high)."""
    session = SessionLocal()
    try:
        # Retrieve all boxes sorted by box ID in ascending order
        boxes = session.query(BoxModel).order_by(BoxModel.id.asc()).all()
        if boxes:
            # Prepare data for boxes
            box_headers = ["Box ID", "Description", "Height", "Length", "Weight", "Location", "Tags", "Picture"]
            box_rows = []
            for box in boxes:
                box_rows.append([
                    box.id,
                    box.box_description or '',
                    box.box_height or '',
                    box.box_length or '',
                    box.box_weight or '',
                    box.box_location or '',
                    box.box_user_defined_tags or '',
                    box.box_picture or ''
                ])
            # Print boxes table
            click.echo(tabulate(box_rows, headers=box_headers, tablefmt="plain"))

            for box in boxes:
                # Retrieve items in the box, sorted by item ID
                items = session.query(BoxItemModel).filter_by(box_id=box.id).order_by(BoxItemModel.id.asc()).all()
                if items:
                    # Prepare data for items
                    item_headers = ["Item ID", "Description", "Height", "Length", "Weight", "Location", "Tags", "Picture"]
                    item_rows = []
                    for item in items:
                        item_rows.append([
                            item.id,
                            item.item_description or '',
                            item.item_height or '',
                            item.item_length or '',
                            item.item_weight or '',
                            item.item_location or '',
                            item.item_user_defined_tags or '',
                            item.item_picture or ''
                        ])
                    # Print items table with a title
                    click.echo(f"\nItems in Box ID {box.id}:")
                    click.echo(tabulate(item_rows, headers=item_headers, tablefmt="plain"))
                else:
                    click.echo(f"\nNo items in Box ID {box.id}.")
        else:
            click.echo('No boxes found.')
    finally:
        session.close()