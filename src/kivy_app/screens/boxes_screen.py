from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.logger import Logger

from src.database import SessionLocal
from src.models import BoxModel
from src.box import Box
from src.utils.alias_utils import load_aliases, generate_unique_alias


class BoxesScreen(Screen):
    def on_pre_enter(self):
        Logger.debug("BoxesScreen: on_pre_enter() called")
        self.display_boxes()

    def display_boxes(self):
        Logger.debug("BoxesScreen: display_boxes() called")
        session = SessionLocal()
        self.ids.boxes_results_box.clear_widgets()

        try:
            # Fetch all boxes
            boxes = session.query(BoxModel).all()
            Logger.debug(f"BoxesScreen: Found {len(boxes)} boxes")

            if boxes:
                grid = GridLayout(cols=5, size_hint_y=None, row_default_height=40)
                grid.bind(minimum_height=grid.setter('height'))

                # Header row
                grid.add_widget(Label(text="Alias"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))
                grid.add_widget(Label(text="Actions"))

                for box in boxes:
                    grid.add_widget(Label(text=box.alias))
                    grid.add_widget(Label(text=box.box_location or "N/A"))
                    grid.add_widget(Label(text=str(box.box_weight) if box.box_weight else "N/A"))
                    grid.add_widget(Label(text=box.box_description or "N/A"))

                    # Edit and Delete buttons
                    actions = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)

                    edit_button = Button(text="Edit", size_hint_x=None, width=50)
                    edit_button.bind(on_press=lambda _, b=box: self.show_edit_popup(b))
                    actions.add_widget(edit_button)

                    delete_button = Button(text="Delete", size_hint_x=None, width=50)
                    delete_button.bind(on_press=lambda _, b=box: self.show_delete_popup(b))
                    actions.add_widget(delete_button)

                    grid.add_widget(actions)

                scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
                scrollview.add_widget(grid)
                self.ids.boxes_results_box.add_widget(scrollview)
            else:
                self.ids.boxes_results_box.add_widget(Label(text="No boxes found"))
        except Exception as e:
            Logger.error(f"BoxesScreen: Error displaying boxes - {e}")
        finally:
            session.close()

    def show_add_box_popup(self):
        Logger.debug("BoxesScreen: show_add_box_popup() called")

        # Main popup layout
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Description and Location on the same line
        basic_fields_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        description_input = TextInput(hint_text="Description", multiline=False, size_hint_x=0.8)
        location_input = TextInput(hint_text="Location", multiline=False, size_hint_x=0.2)
        basic_fields_layout.add_widget(description_input)
        basic_fields_layout.add_widget(location_input)
        popup_layout.add_widget(Label(text="Description and Location"))
        popup_layout.add_widget(basic_fields_layout)

        # Additional fields (initially hidden)
        additional_fields_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        advanced_fields = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        height_input = TextInput(hint_text="Height", multiline=False, size_hint_x=0.33)
        length_input = TextInput(hint_text="Length", multiline=False, size_hint_x=0.33)
        weight_input = TextInput(hint_text="Weight", multiline=False, size_hint_x=0.33)
        advanced_fields.add_widget(height_input)
        advanced_fields.add_widget(length_input)
        advanced_fields.add_widget(weight_input)
        additional_fields_layout.add_widget(Label(text="Height, Length, and Weight"))
        additional_fields_layout.add_widget(advanced_fields)

        # Initially hide additional fields
        additional_fields_layout.opacity = 0
        additional_fields_layout.disabled = True

        # Show additional fields button
        def toggle_additional_fields(instance):
            if additional_fields_layout.opacity == 0:
                additional_fields_layout.opacity = 1  # Show
                additional_fields_layout.disabled = False  # Enable interaction
                instance.text = "Hide Additional Fields"
            else:
                additional_fields_layout.opacity = 0  # Hide
                additional_fields_layout.disabled = True  # Disable interaction
                instance.text = "Show Additional Fields"

        toggle_button = Button(text="Show Additional Fields", size_hint_y=None, height=40)
        toggle_button.bind(on_press=toggle_additional_fields)
        popup_layout.add_widget(toggle_button)

        # Add additional fields to the layout
        popup_layout.add_widget(additional_fields_layout)

        # Buttons for save/cancel
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_button = Button(text="Save")
        save_button.bind(on_press=lambda _: self.add_box(
            description_input.text,
            location_input.text,
            height_input.text,
            length_input.text,
            weight_input.text
        ))
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(button_layout)
        popup = Popup(title="Add Box", content=popup_layout, size_hint=(0.8, 0.8))
        popup.open()

    def add_box(self, description, location, height, length, weight):
        Logger.debug("BoxesScreen: add_box() called")
        session = SessionLocal()
        try:
            alias_dict = load_aliases()
            theme = "animals"

            # Generate a unique alias
            alias = generate_unique_alias(session, BoxModel, theme, alias_dict, is_box=True)

            # Create new box
            new_box = BoxModel(
                alias=alias,
                box_description=description,
                box_location=location,
                box_height=float(height) if height else None,
                box_length=float(length) if length else None,
                box_weight=float(weight) if weight else None,
                box_QRcode=Box.generate_random_qrcode()
            )

            session.add(new_box)
            session.commit()
            Logger.info(f"BoxesScreen: Box added successfully with alias '{alias}'")
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to add box - {e}")
            session.rollback()
        finally:
            session.close()
        self.display_boxes()

    def show_edit_popup(self, box):
        Logger.debug(f"BoxesScreen: show_edit_popup() called for Alias {box.alias}")

        # Main popup layout
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Description and Location on the same line
        basic_fields_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        description_input = TextInput(text=box.box_description, multiline=False, size_hint_x=0.8)
        location_input = TextInput(text=box.box_location, multiline=False, size_hint_x=0.2)
        basic_fields_layout.add_widget(description_input)
        basic_fields_layout.add_widget(location_input)
        popup_layout.add_widget(Label(text="Description and Location"))
        popup_layout.add_widget(basic_fields_layout)

        # Additional fields (initially hidden)
        additional_fields_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        advanced_fields = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        height_input = TextInput(text=str(box.box_height) if box.box_height else "", multiline=False, size_hint_x=0.33)
        length_input = TextInput(text=str(box.box_length) if box.box_length else "", multiline=False, size_hint_x=0.33)
        weight_input = TextInput(text=str(box.box_weight) if box.box_weight else "", multiline=False, size_hint_x=0.33)
        advanced_fields.add_widget(height_input)
        advanced_fields.add_widget(length_input)
        advanced_fields.add_widget(weight_input)
        additional_fields_layout.add_widget(Label(text="Height, Length, and Weight"))
        additional_fields_layout.add_widget(advanced_fields)

        # Initially hide additional fields
        additional_fields_layout.opacity = 0
        additional_fields_layout.disabled = True

        # Show additional fields button
        def toggle_additional_fields(instance):
            if additional_fields_layout.opacity == 0:
                additional_fields_layout.opacity = 1  # Show
                additional_fields_layout.disabled = False  # Enable interaction
                instance.text = "Hide Additional Fields"
            else:
                additional_fields_layout.opacity = 0  # Hide
                additional_fields_layout.disabled = True  # Disable interaction
                instance.text = "Show Additional Fields"

        toggle_button = Button(text="Show Additional Fields", size_hint_y=None, height=40)
        toggle_button.bind(on_press=toggle_additional_fields)
        popup_layout.add_widget(toggle_button)

        # Add additional fields to the layout
        popup_layout.add_widget(additional_fields_layout)

        # Buttons for save/cancel
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_button = Button(text="Save")
        save_button.bind(on_press=lambda _: self.edit_box(
            box,
            description_input.text,
            location_input.text,
            height_input.text,
            length_input.text,
            weight_input.text
        ))
        button_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(button_layout)
        popup = Popup(title=f"Edit Box {box.alias}", content=popup_layout, size_hint=(0.8, 0.8))
        popup.open()

    def edit_box(self, box, description, location, height, length, weight):
        Logger.debug(f"BoxesScreen: edit_box() called for Alias {box.alias}")
        session = SessionLocal()
        try:
            box.box_description = description
            box.box_location = location
            box.box_height = float(height) if height else None
            box.box_length = float(length) if length else None
            box.box_weight = float(weight) if weight else None

            session.merge(box)
            session.commit()
            Logger.info(f"BoxesScreen: Box with alias {box.alias} updated successfully.")
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to update box - {e}")
            session.rollback()
        finally:
            session.close()
        self.display_boxes()

    def show_delete_popup(self, box):
        Logger.debug(f"BoxesScreen: show_delete_popup() called for Alias {box.alias}")

        # Confirmation popup layout
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_layout.add_widget(Label(text=f"Are you sure you want to delete the box '{box.alias}'?"))

        # Buttons for Yes/No
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

        yes_button = Button(text="Yes")
        yes_button.bind(on_press=lambda _: self.delete_box(box))
        yes_button.bind(on_press=lambda _: popup.dismiss())  # Close popup on Yes
        button_layout.add_widget(yes_button)

        no_button = Button(text="No")
        no_button.bind(on_press=lambda _: popup.dismiss())  # Close popup on No
        button_layout.add_widget(no_button)

        popup_layout.add_widget(button_layout)

        # Create and display popup
        popup = Popup(title="Confirm Delete", content=popup_layout, size_hint=(0.6, 0.4))
        popup.open()

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
