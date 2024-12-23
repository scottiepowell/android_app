import io
import os
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from src.database import SessionLocal
from src.models import BoxModel, BoxItemModel
from src.kivy_app.screens.boxes_screen_popups import show_add_box_popup, show_edit_popup, show_delete_popup, show_view_popup
from src.image import ImageHandler
from src.utils.alias_utils import sort_aliases

class BoxesScreen(Screen):
    def on_pre_enter(self):
        Logger.debug("BoxesScreen: on_pre_enter() called")
        self.display_boxes()

    def display_boxes(self):
        Logger.debug("BoxItemsScreen: display_boxes() called")
        session = SessionLocal()
        self.ids.boxes_results_box.clear_widgets()

        # Load default image for placeholder
        default_image_data = ImageHandler.resolve_asset("assets/na.jpeg")
        default_texture = CoreImage(io.BytesIO(default_image_data), ext="jpeg").texture

        try:
            boxes = session.query(BoxModel).all()
            Logger.debug(f"BoxItemsScreen: Found {len(boxes)} boxes")

            if boxes:

                # Sort boxes by alias using sort_aliases
                aliases = [box.alias for box in boxes if box.alias]
                sorted_aliases = sort_aliases(aliases)

                # Sort the boxes list based on sorted aliases
                boxes = sorted(boxes, key=lambda box: sorted_aliases.index(
                    box.alias) if box.alias in sorted_aliases else float('inf'))

                # GridLayout for displaying boxes
                grid = GridLayout(cols=1, size_hint_y=None, spacing=20, padding=[10, 10])
                grid.bind(minimum_height=grid.setter('height'))

                for box in boxes:
                    box_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10, padding=[10, 10])
                    box_container.bind(minimum_height=box_container.setter('height'))

                    # Create the header layout
                    header_layout = GridLayout(cols=3, size_hint_y=None, spacing=10)
                    header_layout.bind(minimum_height=header_layout.setter('height'))

                    # Alias column (example)
                    header_layout.add_widget(Label(text=box.alias, size_hint_x=0.2))

                    # Picture column (example)
                    if box.box_thumbnail:
                        thumbnail_texture = ImageHandler.bytes_to_texture(box.box_thumbnail)
                    else:
                        thumbnail_texture = default_texture

                    picture = Image(texture=thumbnail_texture, size_hint=(0.3, None), height=100)
                    header_layout.add_widget(picture)

                    # Actions column
                    actions_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_x=0.5)
                    expand_button = Button(text="+", size_hint=(None, None), size=(30, 30))
                    collapse_button = Button(text="-", size_hint=(None, None), size=(30, 30))
                    collapse_button.opacity = 0  # Initially hidden
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

                    # Now add header_layout to the box_container
                    box_container.add_widget(header_layout)

                    # Create the box_items_layout and add it now
                    box_items_layout = GridLayout(cols=3, size_hint_y=None, row_default_height=80, spacing=10)
                    box_items_layout.bind(minimum_height=box_items_layout.setter('height'))
                    box_items_layout.opacity = 0
                    box_items_layout.disabled = True

                    box_container.add_widget(box_items_layout)

                    def load_box_items(current_box=box):
                        box_items_layout.clear_widgets()
                        with SessionLocal() as new_session:
                            items = new_session.query(BoxItemModel).filter_by(box_id=current_box.id).all()
                            if items:
                                for item in items:
                                    box_items_layout.add_widget(Label(text=item.alias, size_hint_x=0.3))
                                    picture = Image(texture=default_texture, size_hint=(0.3, None), height=80)
                                    box_items_layout.add_widget(picture)
                                    actions = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None)
                                    actions.bind(minimum_height=actions.setter('height'))
                                    actions.add_widget(Button(text="Edit", size_hint=(None, None), size=(60, 30)))
                                    actions.add_widget(Button(text="Delete", size_hint=(None, None), size=(60, 30)))
                                    actions.add_widget(Button(text="View", size_hint=(None, None), size=(60, 30)))
                                    box_items_layout.add_widget(actions)
                            else:
                                box_items_layout.add_widget(
                                    Label(text="No box items found", size_hint_y=None, height=40, halign='center'))

                    def expand(instance, current_box=box):
                        load_box_items(current_box)

                        # Show the box_items_layout
                        box_items_layout.opacity = 1
                        box_items_layout.disabled = False

                        # Update heights based on the newly visible items
                        box_items_layout.height = box_items_layout.minimum_height
                        box_container.height = box_container.minimum_height
                        grid.height = grid.minimum_height

                        # Toggle button states
                        expand_button.opacity = 0
                        expand_button.disabled = True
                        collapse_button.opacity = 1
                        collapse_button.disabled = False

                        # Force layout update after changes
                        Clock.schedule_once(lambda dt: self.ids.boxes_results_box.do_layout())
                        Clock.schedule_once(lambda dt: grid.do_layout())
                        # If necessary, also re-scroll to the item, so the user sees it in the right place:
                        # Clock.schedule_once(lambda dt: scrollview.scroll_to(box_container))

                    def collapse(instance, current_box=box):
                        # Hide the box_items_layout
                        box_items_layout.opacity = 0
                        box_items_layout.disabled = True

                        # Update heights again
                        box_items_layout.height = 0  # or just leave it as is and rely on opacity
                        box_container.height = box_container.minimum_height
                        grid.height = grid.minimum_height

                        # Toggle button states
                        expand_button.opacity = 1
                        expand_button.disabled = False
                        collapse_button.opacity = 0
                        collapse_button.disabled = True

                        # Force layout update after changes
                        Clock.schedule_once(lambda dt: self.ids.boxes_results_box.do_layout())
                        Clock.schedule_once(lambda dt: grid.do_layout())

                    # Bind the buttons after they're defined
                    expand_button.bind(on_press=lambda instance, current_box=box: expand(instance, current_box))
                    collapse_button.bind(on_press=lambda instance, current_box=box: collapse(instance, current_box))

                    grid.add_widget(box_container)

                self.ids.boxes_results_box.clear_widgets()
                self.ids.boxes_results_box.add_widget(grid)
            else:
                self.ids.boxes_results_box.add_widget(Label(text="No boxes found."))
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Error displaying boxes - {e}")
        finally:
            session.close()

    def show_add_box_popup(self):
        show_add_box_popup(self)

    def show_edit_box_popup(self):
        show_add_box_popup(self)

    def show_delete_box_popup(self):
        show_delete_popup(self)
