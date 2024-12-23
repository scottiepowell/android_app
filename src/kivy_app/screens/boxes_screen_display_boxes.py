# boxes_screens_display_boxes.py

import io
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from src.database import SessionLocal
from src.models import BoxModel
from src.image import ImageHandler
from src.kivy_app.screens.boxes_screen_popups import show_view_popup, show_edit_popup, show_delete_popup, show_alias_edit_popup
from src.utils.alias_utils import load_aliases, find_theme_for_box, sort_aliases

class BoxesScreenDisplayBoxes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alias_dict = load_aliases()
        Logger.debug(f"Alias Dictionary Loaded: {self.alias_dict}")
        self.current_theme = None

    def on_pre_enter(self, *args):
        Logger.debug("BoxesScreenDisplayBoxes: on_pre_enter - Querying database and displaying boxes")
        self.ids.main_container.clear_widgets()

        # Database logic:
        session = SessionLocal()
        # Load default image for placeholder
        default_image_data = ImageHandler.resolve_asset("assets/na.jpeg")
        default_texture = CoreImage(io.BytesIO(default_image_data), ext="jpeg").texture

        try:
            boxes = session.query(BoxModel).all()
            Logger.debug(f"BoxesScreenDisplayBoxes: Found {len(boxes)} boxes in the database")

            if boxes:
                # extract aliases and sort them using updated utility
                # Ensure all aliases (predefined and user-created) are included in the sorting
                for box in boxes:
                    if box.alias and box.alias not in sort_aliases:
                        sort_aliases.append(box.alias)

                # Sort the boxes based on the complete sorted_aliases list
                boxes = sorted(boxes, key=lambda box: sort_aliases.index(
                    box.alias) if box.alias in sort_aliases else float('inf'))

                # For each box, we will create a box UI using create_box.
                # We'll still pass the same hard-coded items for demonstration.
                hard_coded_items = ["ShortAlias", "ThisIsAVeryLongItemAliasName", "BoxItemC"]

                for i, db_box in enumerate(boxes):
                    box_alias = db_box.alias if db_box.alias else "UnknownBox"

                    # Determine the theme for the current box
                    try:
                        box_theme = find_theme_for_box(session, db_box.id, self.alias_dict)
                        Logger.debug(f"Theme for Box ID {db_box.id} ('{box_alias}'): {box_theme}")
                    except ValueError as e:
                        Logger.warning(f"Could not determine theme for Box ID {db_box.id}: {e}")
                        box_theme = "UnknownTheme"

                    if db_box.box_thumbnail:
                        try:
                            image_data = db_box.box_thumbnail
                            thumbnail_texture = ImageHandler.resize_to_100_100(image_data, (100, 100))
                        except Exception as e:
                            Logger.error(f"Error loading thumbnail for box {box_alias}: {e}")
                            thumbnail_texture = default_texture
                    else:
                        thumbnail_texture = default_texture

                    # Now call create_box for each database box
                    # Note: create_box currently doesn't accept textures directly, it uses a fixed image source.
                    # We will slightly modify create_box to accept a box_alias and a thumbnail_texture.
                    self.create_box(db_box, i, boxes, hard_coded_items, thumbnail_texture,box_theme)
            else:
                # No boxes found
                self.ids.main_container.add_widget(Label(text="No boxes found."))
        except Exception as e:
            Logger.error(f"BoxesScreenDisplayBoxes: Error displaying boxes - {e}")
        finally:
            session.close()

    def create_box(self, db_box, box_index, boxes_list, items, thumbnail_texture,box_theme):
        """
           db_box: the BoxModel database object
           box_index: the current index of this box in boxes_list
           boxes_list: the full list of boxes, so we can reference them in the view popup
           items: the hard-coded item list
           thumbnail_texture: the resized or default texture for the box picture
           """
        box_alias = db_box.alias if db_box.alias else "UnknownBox"
        Logger.debug(f"BoxesScreenDisplayBoxes: Creating UI for box '{box_alias}'")

        box_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10, padding=[10, 10])
        box_container.bind(minimum_height=box_container.setter('height'))

        # Adjusted layout hints for the header
        header_layout = GridLayout(cols=3, size_hint_y=None, spacing=5, padding=[0, 0, 0, 0])
        header_layout.bind(minimum_height=header_layout.setter('height'))

        # Alias column
        alias_label = Label(text=db_box.alias if db_box.alias else "UnknownBox", size_hint=(0.15, None), height=30)
        alias_label.bind(on_touch_down=lambda instance, touch: self.alias_label_clicked(instance, touch, db_box,box_theme))
        header_layout.add_widget(alias_label)

        # Picture column (use thumbnail_texture from DB or fallback)
        box_picture = Image(texture=thumbnail_texture, size_hint=(0.25, None), height=100)
        header_layout.add_widget(box_picture)

        # Actions column
        actions_layout = BoxLayout(orientation="horizontal", spacing=5, size_hint=(0.6, None), height=50)

        expand_button = Button(text="+", size_hint=(None, None), size=(30, 30), background_color=(1, 0, 0, 1))
        collapse_button = Button(text="-", size_hint=(None, None), size=(30, 30), background_color=(0, 1, 0, 1))
        collapse_button.opacity = 0
        collapse_button.disabled = True

        edit_button = Button(text="Edit", size_hint=(None, None), size=(60, 30))
        delete_button = Button(text="Delete", size_hint=(None, None), size=(60, 30))
        view_button = Button(text="View", size_hint=(None, None), size=(60, 30))

        actions_layout.add_widget(expand_button)
        actions_layout.add_widget(collapse_button)
        actions_layout.add_widget(edit_button)
        actions_layout.add_widget(delete_button)
        actions_layout.add_widget(view_button)

        header_layout.add_widget(actions_layout)
        box_container.add_widget(header_layout)

        # Indented items layout
        items_container = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=5, padding=[20, 0, 0, 0])
        items_container.bind(minimum_height=items_container.setter('height'))

        box_items_layout = GridLayout(cols=3, size_hint_y=None, spacing=5)
        box_items_layout.bind(minimum_height=box_items_layout.setter('height'))
        box_items_layout.opacity = 0
        box_items_layout.disabled = True

        items_container.add_widget(box_items_layout)
        box_container.add_widget(items_container)

        def truncate_alias(alias):
            if len(alias) > 15:
                return alias[:15] + '...'
            return alias

        def load_items(bn_alias, box_items, bil):
            Logger.debug(f"BoxesScreenDisplayBoxes: load_items called for Box '{bn_alias}'. Items: {box_items}")
            bil.clear_widgets()
            for it in box_items:
                Logger.debug(f"BoxesScreenDisplayBoxes: Adding {it} to Box '{bn_alias}'")
                truncated_alias = truncate_alias(it)

                alias_label = Label(text=truncated_alias, size_hint_x=0.3, size_hint_y=None, height=30)
                bil.add_widget(alias_label)

                item_picture = Image(source="assets/na.jpeg", size_hint=(0.3, None), height=60)
                bil.add_widget(item_picture)

                item_actions_layout = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=30)
                item_edit_btn = Button(text="Edit", size_hint=(None, None), size=(60, 30))
                item_delete_btn = Button(text="Delete", size_hint=(None, None), size=(60, 30))
                item_view_btn = Button(text="View", size_hint=(None, None), size=(60, 30))

                item_actions_layout.add_widget(item_edit_btn)
                item_actions_layout.add_widget(item_delete_btn)
                item_actions_layout.add_widget(item_view_btn)

                bil.add_widget(item_actions_layout)

            bil.height = bil.minimum_height
            Logger.debug(f"BoxesScreenDisplayBoxes: After loading items for Box '{bn_alias}', bil.height={bil.height}")

        def expand(_instance):
            Logger.debug(f"BoxesScreenDisplayBoxes: expand called for Box '{box_alias}'")

            # Switch from expand to collapse
            if expand_button in actions_layout.children:
                Logger.debug(f"(Box '{box_alias}') Removing expand_button from actions_layout")
                actions_layout.remove_widget(expand_button)
            if collapse_button not in actions_layout.children:
                Logger.debug(f"(Box '{box_alias}') Adding collapse_button to actions_layout")
                actions_layout.add_widget(collapse_button, index=1)

            collapse_button.opacity = 1
            collapse_button.disabled = False

            load_items(box_alias, items, box_items_layout)
            box_items_layout.opacity = 1
            box_items_layout.disabled = False
            box_items_layout.height = box_items_layout.minimum_height
            box_container.height = box_container.minimum_height
            actions_layout.do_layout()
            header_layout.do_layout()

        def collapse(_instance):
            Logger.debug(f"BoxesScreenDisplayBoxes: collapse called for Box '{box_alias}'")

            # Switch back to expand
            if collapse_button in actions_layout.children:
                Logger.debug(f"(Box '{box_alias}') Removing collapse_button from actions_layout")
                actions_layout.remove_widget(collapse_button)
            if expand_button not in actions_layout.children:
                Logger.debug(f"(Box '{box_alias}') Adding expand_button to actions_layout")
                actions_layout.add_widget(expand_button, index=0)

            expand_button.opacity = 1
            expand_button.disabled = False

            box_items_layout.opacity = 0
            box_items_layout.disabled = True
            box_items_layout.height = 0
            box_container.height = box_container.minimum_height
            actions_layout.do_layout()
            header_layout.do_layout()

        expand_button.bind(on_press=expand)
        collapse_button.bind(on_press=collapse)

        # 'View' button
        view_button.bind(
            on_press=lambda instance:
            show_view_popup(db_box, boxes_list, box_index, self)
        )

        # 'Edit' button
        edit_button.bind(
            on_press=lambda instance:
            show_edit_popup(self, db_box)
        )

        # 'Delete' button
        delete_button.bind(
            on_press=lambda instance:
            show_delete_popup(self, db_box)
        )

        self.ids.main_container.add_widget(box_container)
        Logger.debug(f"BoxesScreenDisplayBoxes: Finished setting up Box '{box_alias}'")

    def delete_box(self, box):
        """Delete the given box from the database, then refresh the display."""
        Logger.debug(f"BoxesScreenDisplayBoxes: delete_box() called for Alias {box.alias}")

        # Open a session to delete the box
        session = SessionLocal()
        try:
            # Retrieve the box in case it's a detached object
            db_box = session.query(BoxModel).filter_by(id=box.id).first()
            if not db_box:
                Logger.error(f"Box with ID {box.id} not found. Cannot delete.")
                return

            # Delete the box
            session.delete(db_box)
            session.commit()
            Logger.info(f"Box with alias '{box.alias}' was deleted.")

            # Refresh the boxes display
            self.on_pre_enter()
        except Exception as e:
            Logger.error(f"Error deleting box alias '{box.alias}': {e}")
            session.rollback()
        finally:
            session.close()

    def alias_label_clicked(self, instance, touch, db_box,box_theme):
        """Handles clicks on the alias label."""
        if instance.collide_point(*touch.pos):  # Check if the touch is within the label's bounds
            Logger.debug(f"Alias label clicked for Box ID {db_box.id}")
            show_alias_edit_popup(self, db_box, box_theme)

