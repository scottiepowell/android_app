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
from src.kivy_app.screens.boxes_screen_popups import show_add_box_popup, show_edit_popup, show_delete_popup, show_view_popup
from src.image import ImageHandler


class BoxesScreen(Screen):
    def on_pre_enter(self):
        Logger.debug("BoxesScreen: on_pre_enter() called")
        self.display_boxes()

    def display_boxes(self):
        Logger.debug("BoxesScreen: display_boxes() called")
        session = SessionLocal()
        self.ids.boxes_results_box.clear_widgets()

        Logger.debug(f"Initial boxes_results_box size: {self.ids.boxes_results_box.size}")

        # Load default image data and texture
        default_image_data = ImageHandler.resolve_asset("assets/na.jpeg")
        resized_default_data = ImageHandler.resize_default_thumbnail(default_image_data, size=(100, 100))
        default_texture = CoreImage(io.BytesIO(resized_default_data), ext="jpeg").texture

        try:
            boxes = session.query(BoxModel).all()
            Logger.debug(f"BoxesScreen: Found {len(boxes)} boxes")

            if boxes:
                # Create GridLayout and ScrollView before the loop
                grid = GridLayout(cols=3, size_hint_y=None, row_default_height=100)
                grid.bind(minimum_height=grid.setter('height'))

                # Add headers
                grid.add_widget(Label(text="Alias", size_hint_x=0.2))
                grid.add_widget(Label(text="Picture", size_hint_x=0.3))
                grid.add_widget(Label(text="Actions", size_hint_x=0.5))

                # Populate GridLayout with box data
                for i, box in enumerate(boxes):  # Use enumerate to track index
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
                    actions = BoxLayout(
                        orientation='horizontal',
                        size_hint_x=0.5,
                        size_hint_y=1,  # Allow BoxLayout to take up full height of the grid row
                        spacing=20,  # Add spacing between buttons
                        padding=[10, 0, 10, 0]  # Add padding inside the BoxLayout
                    )

                    # Add Edit, Delete, and View buttons
                    edit_button = Button(text="Edit", size_hint=(1, None), height=30, pos_hint={"center_y": 0.5})
                    delete_button = Button(text="Delete", size_hint=(1, None), height=30, pos_hint={"center_y": 0.5})
                    view_button = Button(text="View", size_hint=(1, None), height=30, pos_hint={"center_y": 0.5})

                    # Bind buttons to their respective actions
                    edit_button.bind(on_press=lambda instance, b=box: show_edit_popup(self, b))
                    delete_button.bind(on_press=lambda instance, b=box: show_delete_popup(self, b))
                    view_button.bind(on_press=lambda instance, b=box, idx=i: show_view_popup(b, boxes, idx, self))

                    # Add buttons to the actions box
                    actions.add_widget(edit_button)
                    actions.add_widget(delete_button)
                    actions.add_widget(view_button)

                    # Add actions box to the grid
                    grid.add_widget(actions)

                # Create ScrollView and add GridLayout
                scrollview = ScrollView(size_hint=(1, 1))
                scrollview.add_widget(grid)

                Logger.debug(f"ScrollView size before adding: {scrollview.size}")
                Logger.debug(f"Grid size: {grid.size}")

                self.ids.boxes_results_box.add_widget(scrollview)

                Logger.debug(f"boxes_results_box size after adding ScrollView: {self.ids.boxes_results_box.size}")

            else:
                # If no boxes, display a message
                self.ids.boxes_results_box.add_widget(Label(text="No boxes found"))
        except Exception as e:
            Logger.error(f"BoxesScreen: Error displaying boxes - {e}")
        finally:
            session.close()

    def show_add_box_popup(self):
        show_add_box_popup(self)

    def show_edit_box_popup(self):
        show_add_box_popup(self)

    def show_delete_box_popup(self):
        show_delete_popup(self)
