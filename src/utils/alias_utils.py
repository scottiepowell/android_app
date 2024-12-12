import csv
import os
from collections import defaultdict


def normalize_theme_name(theme_name):
    """Normalize a theme name by removing prefixes and converting to lowercase."""
    return theme_name.replace("alias_", "").lower()

def load_aliases(directory_name="alias"):
    """Load aliases from multiple CSV files into a structured dictionary."""
    # Dynamically locate the assets directory, going up two levels
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "..", "..", "assets", directory_name)

    if not os.path.exists(assets_dir):
        raise FileNotFoundError(f"Alias directory not found: {assets_dir}")

    alias_dict = defaultdict(list)
    for file_name in os.listdir(assets_dir):
        if file_name.endswith(".csv"):
            file_path = os.path.join(assets_dir, file_name)
            theme = os.path.splitext(file_name)[0]
            normalized_theme = normalize_theme_name(theme)
            with open(file_path, mode="r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row["Alias"]:
                        alias_dict[normalized_theme].append(row["Alias"].lower())

    # Alphabetically sort the aliases for each theme
    for theme in alias_dict:
        alias_dict[theme].sort()

    return alias_dict

def find_theme_for_box(session, box_id, alias_dict):
    """
    Find the theme of the box by its alias. Normalize to base theme if needed.
    Fallback: use reverse-sorted themes and pick the last available theme.
    """
    from src.models import BoxModel  # Avoid circular imports

    # Get the box's alias
    box = session.query(BoxModel).filter_by(id=box_id).first()
    if not box:
        raise ValueError(f"Box with ID {box_id} not found.")

    box_theme = box.alias

    # Normalize back to base theme if alias includes suffix (e.g., animals01 -> animals)
    for theme in alias_dict:
        if box_theme.startswith(theme):
            return theme

    # If no match found, use reverse-sorted themes and pick the last one
    sorted_themes = sorted(alias_dict.keys(), reverse=True)
    for theme in sorted_themes:
        if theme in alias_dict:
            return theme

    raise ValueError("No valid theme found for box items.")

def generate_unique_alias(session, model, theme, alias_dict, is_box=False):
    """Generate a unique alias from a given theme."""
    if theme not in alias_dict or not alias_dict[theme]:
        raise ValueError(f"No aliases available in theme '{theme}'.")

    # Sort themes alphabetically
    sorted_themes = sorted(alias_dict.keys())

    if is_box:
        # Find the next available theme for the box
        return find_next_available_theme(session, model, sorted_themes, alias_dict)

    # For box items, iterate over aliases in the current theme
    for base_alias in alias_dict[theme]:
        if not session.query(model).filter_by(alias=base_alias).first():
            return base_alias

    # If all aliases for box items are taken, generate a numerical suffix
    count = 2
    while True:
        for base_alias in alias_dict[theme]:
            alias_with_suffix = f"{base_alias}{count:02d}"
            if not session.query(model).filter_by(alias=alias_with_suffix).first():
                return alias_with_suffix
        count += 1


def find_next_available_theme(session, model, sorted_themes, alias_dict):
    """
    Find the next available theme alias for a box.
    If all themes are assigned, create a new one with a numerical suffix.
    """
    # Check for available base themes first
    for theme in sorted_themes:
        if not session.query(model).filter_by(alias=theme).first():
            return theme

    # If all base themes are taken, generate new ones with numerical suffixes
    count = 2
    while True:
        for theme in sorted_themes:
            theme_with_suffix = f"{theme}{count:02d}"  # e.g., animals02
            if not session.query(model).filter_by(alias=theme_with_suffix).first():
                return theme_with_suffix
        count += 1