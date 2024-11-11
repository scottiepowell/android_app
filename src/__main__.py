#kivy/src/__main__.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import click
from commands.find import find
from commands.add import add
from commands.edit import edit
from commands.delete import delete
from database import init_db

@click.group()
def cli():
    pass

cli.add_command(find)
cli.add_command(add)
cli.add_command(edit)
cli.add_command(delete)

if __name__ == '__main__':
    init_db()
    cli()
