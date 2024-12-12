import os

# Define a single source of truth for the database path
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'whats_in_the_box.db'))
