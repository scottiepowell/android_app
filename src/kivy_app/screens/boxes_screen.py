import io
import os
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
from src.models import BoxModel
from src.kivy_app.screens.boxes_screen_popups import show_add_box_popup, show_edit_popup, show_delete_popup
from src.image import ImageHandler


class BoxesScreen(Screen):
    def on_pre_enter(self):
        Logger.debug("BoxesScreen: on_pre_enter() called")
        self.display_boxes()

    def display_boxes(self):
        Logger.debug("BoxesScreen: display_boxes() called")
        session = SessionLocal()
        self.ids.boxes_results_box.clear_widgets()

        # Load default image data and texture
        default_image_data = ImageHandler.resolve_asset("assets/na.jpeg")
        default_texture = CoreImage(io.BytesIO(default_image_data), ext="jpeg").texture

        try:
            boxes = session.query(BoxModel).all()
            Logger.debug(f"BoxesScreen: Found {len(boxes)} boxes")

            if boxes:
                # Define the grid layout with 3 columns: Alias, Picture, and Actions
                grid = GridLayout(cols=3, size_hint_y=None, row_default_height=100)
                grid.bind(minimum_height=grid.setter('height'))

                # Add headers
                grid.add_widget(Label(text="Alias", size_hint_x=0.2))  # Fixed width for Alias
                grid.add_widget(Label(text="Picture", size_hint_x=0.3))  # Space for Picture
                grid.add_widget(Label(text="Actions", size_hint_x=0.5))  # More space for Actions

                for box in boxes:
                    # Alias column
                    grid.add_widget(Label(text=box.alias, size_hint_x=0.2))

                    # Picture column
                    try:
                        if box.box_thumbnail:
                            thumbnail_texture = ImageHandler.bytes_to_texture(box.box_thumbnail)
                        else:
                            thumbnail_texture = default_texture
                    except Exception as e:
                        Logger.error(f"Failed to load thumbnail for box {box.alias}: {e}")
                        thumbnail_texture = default_texture

                    picture = Image(texture=thumbnail_texture, size_hint=(0.3, None), height=100)
                    grid.add_widget(picture)

                    # Actions column
                    actions = BoxLayout(orientation='horizontal', size_hint_x=0.5, height=30, spacing=10)

                    # Add Edit, Delete, and View buttons
                    edit_button = Button(text="Edit", size_hint_x=None, width=60)
                    delete_button = Button(text="Delete", size_hint_x=None, width=60)
                    view_button = Button(text="View", size_hint_x=None, width=60)  # Placeholder button

                    # Bind buttons to their respective actions
                    edit_button.bind(on_press=lambda instance, b=box: show_edit_popup(self, b))
                    delete_button.bind(on_press=lambda instance, b=box: show_delete_popup(self, b))
                    view_button.bind(on_press=lambda instance, b=box: Logger.debug(
                        f"View button pressed for {b.alias}"))  # Placeholder action

                    # Add buttons to the actions box
                    actions.add_widget(edit_button)
                    actions.add_widget(delete_button)
                    actions.add_widget(view_button)

                    # Add actions box to the grid
                    grid.add_widget(actions)

                # Add the grid to a scrollview
                scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
                scrollview.add_widget(grid)
                self.ids.boxes_results_box.add_widget(scrollview)
            else:
                # If no boxes, display a message
                self.ids.boxes_results_box.add_widget(Label(text="No boxes found"))
        except Exception as e:
            Logger.error(f"BoxesScreen: Error displaying boxes - {e}")
        finally:
            session.close()

    def delete_box(self, box):
        Logger.debug(f"BoxesScreen: delete_box() called for Alias {box.alias}")
        session = SessionLocal()
        try:
            # Delete the box from the database
            session.delete(box)
            session.commit()
            Logger.info(f"BoxesScreen: Box with alias '{box.alias}' deleted successfully.")
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to delete box - {e}")
            session.rollback()
        finally:
            session.close()
        self.display_boxes()

    def show_add_box_popup(self):
        show_add_box_popup(self)

    def show_edit_box_popup(self):
        show_add_box_popup(self)

    def show_delete_box_popup(self):
        show_delete_popup(self)
