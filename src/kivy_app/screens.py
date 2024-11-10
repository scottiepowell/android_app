import os
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from src.box import Box
from src.database import SessionLocal
from src.models import BoxModel, BoxItemModel
from functools import partial

class MainMenuScreen(Screen):
    pass

class AddBoxScreen(Screen):
    def add_box(self):
        box_height = self.ids.box_height.text
        box_length = self.ids.box_length.text
        box_weight = self.ids.box_weight.text
        box_location = self.ids.box_location.text
        box_description = self.ids.box_description.text or "This is a box"

        session = SessionLocal()
        try:
            box = Box(
                box_height=float(box_height),
                box_length=float(box_length),
                box_weight=float(box_weight),
                box_location=box_location,
                box_description=box_description
            )
            box.add_box(session)
            print("Box added successfully")
        finally:
            session.close()

    def clear_inputs(self):
        self.ids.box_height.text = ''
        self.ids.box_length.text = ''
        self.ids.box_weight.text = ''
        self.ids.box_location.text = ''
        self.ids.box_description.text = ''

class FindBoxScreen(Screen):
    def find_boxes(self):
        box_location = self.ids.box_location.text
        session = SessionLocal()
        try:
            results = Box.find_box(session, box_location=box_location)
            self.ids.results_box.clear_widgets()

            if results:
                grid = GridLayout(cols=4, size_hint_y=None, row_default_height=40)
                grid.bind(minimum_height=grid.setter('height'))

                grid.add_widget(Label(text="Box ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))

                for box in results:
                    grid.add_widget(Label(text=str(box.id)))
                    grid.add_widget(Label(text=box.box_location))
                    grid.add_widget(Label(text=str(box.box_weight)))
                    grid.add_widget(Label(text=box.box_description))

                scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
                scrollview.add_widget(grid)
                self.ids.results_box.add_widget(scrollview)
            else:
                self.ids.results_box.add_widget(Label(text="No boxes found"))
        finally:
            session.close()

    def clear_results(self):
        self.ids.box_location.text = ''
        self.ids.results_box.clear_widgets()

class EditBoxScreen(Screen):
    def edit_box(self):
        box_id = self.ids.edit_box_id.text
        box_location = self.ids.edit_box_location.text
        box_description = self.ids.edit_box_description.text

        session = SessionLocal()
        try:
            kwargs = {}
            if box_location:
                kwargs['box_location'] = box_location
            if box_description:
                kwargs['box_description'] = box_description

            box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
            box.edit_box(session, box_id=int(box_id), **kwargs)
            print(f"Box ID: {box_id} edited successfully.")
        finally:
            session.close()

    def clear_inputs(self):
        self.ids.edit_box_id.text = ''
        self.ids.edit_box_location.text = ''
        self.ids.edit_box_description.text = ''

class DeleteBoxScreen(Screen):
    def show_confirm_button(self):
        """Show the confirmation button to confirm deletion."""
        self.ids.confirm_delete_button.opacity = 1
        self.ids.confirm_delete_button.disabled = False

    def delete_box(self):
        """Delete the box from the database based on ID provided."""
        box_id = self.ids.delete_box_id.text

        if not box_id.isdigit():
            print("Invalid Box ID. Please enter a numeric ID.")
            return

        session = SessionLocal()
        try:
            box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
            box.delete_box(session, box_id=int(box_id))
            print(f"Box ID {box_id} deleted successfully.")
        except ValueError as e:
            print(e)
        finally:
            session.close()
            self.clear_inputs()

    def clear_inputs(self):
        """Clear input fields and reset confirm button."""
        self.ids.delete_box_id.text = ''
        self.ids.confirm_delete_button.opacity = 0
        self.ids.confirm_delete_button.disabled = True

class BoxItemsScreen(Screen):
    def on_pre_enter(self):
        self.clear_results()
        self.display_boxes_with_items()

    def display_boxes_with_items(self):
        session = SessionLocal()
        self.ids.boxes_with_items_box.clear_widgets()

        # Find all boxes that have at least one item
        boxes_with_items = (
            session.query(BoxModel)
            .join(BoxItemModel, BoxModel.id == BoxItemModel.box_id)
            .distinct()
            .all()
        )

        if boxes_with_items:
            # Create a GridLayout for displaying boxes in a tabular format
            grid = GridLayout(cols=5, size_hint_y=None, row_default_height=40)
            grid.bind(minimum_height=grid.setter('height'))

            # Add header row with a blank column for "Add Item"
            grid.add_widget(Label(text="", size_hint_x=None, width=30))  # Blank header for "Add Item" column
            grid.add_widget(Label(text="Box ID"))
            grid.add_widget(Label(text="Location"))
            grid.add_widget(Label(text="Weight"))
            grid.add_widget(Label(text="Description"))

            # Add each box's details in rows
            for box in boxes_with_items:
                # Create clickable "Add Item" text
                add_item_label = Label(
                    text="[color=#0000FF][u]Add Item[/u][/color]",  # Blue, underlined text to resemble a link
                    markup=True,
                    size_hint_x=None,
                    width=50,
                    height=30
                )

                # Make label behave as a button
                add_item_label.bind(
                    on_touch_down=lambda lbl, touch, box=box: self.show_add_item_popup(box)
                    if lbl.collide_point(*touch.pos) else None
                )

                # Add "Add Item" link before the box ID
                grid.add_widget(add_item_label)
                grid.add_widget(Label(text=str(box.id)))
                grid.add_widget(Label(text=box.box_location))
                grid.add_widget(Label(text=str(box.box_weight)))
                grid.add_widget(Label(text=box.box_description or ""))

            # Wrap the GridLayout in a ScrollView for scrolling functionality
            scrollview = ScrollView(size_hint=(1, None), size=(self.width, 200))
            scrollview.add_widget(grid)
            self.ids.boxes_with_items_box.add_widget(scrollview)
        else:
            # Show message if no boxes with items found
            self.ids.boxes_with_items_box.add_widget(Label(text="No boxes with items found."))

        session.close()

    def add_item_to_box(self, box, location, weight, description):
        session = SessionLocal()
        try:
            # Add new item to the box
            new_item = BoxItemModel(
                box_id=box.id,
                item_location=location,
                item_weight=float(weight),
                item_description=description
            )
            session.add(new_item)
            session.commit()
            print(f"Item added to Box ID {box.id} successfully.")
        except Exception as e:
            print(f"Failed to add item: {e}")
            session.rollback()
        finally:
            session.close()

        # Refresh the box item list
        self.display_boxes_with_items()

    def show_add_item_popup(self, box):
        # Create a popup layout for adding an item
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Fields to add item details
        location_input = TextInput(multiline=False, hint_text="Location", height=40, size_hint_y=None)
        weight_input = TextInput(multiline=False, hint_text="Weight", height=40, size_hint_y=None)
        description_input = TextInput(multiline=False, hint_text="Description", height=40, size_hint_y=None)

        # Add fields to the content
        content.add_widget(Label(text="Add Item to Box ID " + str(box.id), size_hint_y=None, height=30))
        content.add_widget(Label(text="Location", size_hint_y=None, height=20))
        content.add_widget(location_input)
        content.add_widget(Label(text="Weight", size_hint_y=None, height=20))
        content.add_widget(weight_input)
        content.add_widget(Label(text="Description", size_hint_y=None, height=20))
        content.add_widget(description_input)

        # Buttons to save or cancel
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_button = Button(
            text="Save",
            size_hint_y=None,
            height=40,
            on_press=lambda *args: self.add_item_to_box(box, location_input.text, weight_input.text,
                                                        description_input.text)
        )
        cancel_button = Button(text="Cancel", size_hint_y=None, height=40, on_press=lambda *args: popup.dismiss())

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        # Popup configuration with increased size
        popup = Popup(title="Add Item", content=content, size_hint=(0.9, 0.7))
        popup.open()

    def find_items_by_box_id(self):
        box_id_text = self.ids.box_id_input.text.strip()  # Trim any extra whitespace
        session = SessionLocal()

        try:
            # Clear previous results
            self.ids.items_results_box.clear_widgets()

            if not box_id_text:
                # No box_id entered
                self.ids.items_results_box.add_widget(Label(text="Please enter a Box ID."))
                return

            try:
                box_id = int(box_id_text)
            except ValueError:
                self.ids.items_results_box.add_widget(Label(text="Invalid Box ID. Please enter a valid integer."))
                return

            # Find all items for the given box ID
            items = session.query(BoxItemModel).filter_by(box_id=box_id).all()

            if items:
                # Create a GridLayout for displaying items in a tabular format
                grid = GridLayout(cols=5, size_hint_y=None, row_default_height=30)
                grid.bind(minimum_height=grid.setter('height'))

                # Add header row with a blank column for "Edit"
                grid.add_widget(Label(text="", size_hint_x=None, width=20))  # Blank header for the "Edit" column
                grid.add_widget(Label(text="Item ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))

                # Add each item's details in rows
                for item in items:
                    # Create clickable "Edit" text
                    edit_label = Label(
                        text="[color=#0000FF][u]Edit[/u][/color]",  # Blue, underlined text to resemble a link
                        markup=True,
                        size_hint_x=None,
                        width=20,
                        height=30
                    )

                    # Make label behave as a button
                    edit_label.bind(on_touch_down=lambda lbl, touch, item=item: self.show_edit_popup(item)
                    if lbl.collide_point(*touch.pos) else None)

                    # Add "Edit" link before the item ID
                    grid.add_widget(edit_label)
                    grid.add_widget(Label(text=str(item.id)))
                    grid.add_widget(Label(text=item.item_location))
                    grid.add_widget(Label(text=str(item.item_weight)))
                    grid.add_widget(Label(text=item.item_description or ""))

                # Create a ScrollView and add the GridLayout to it
                scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
                scrollview.add_widget(grid)
                self.ids.items_results_box.add_widget(scrollview)
            else:
                # Show "No items found" message if no items match the box ID
                centered_message = BoxLayout(size_hint=(1, 1), padding=10, orientation='vertical')
                label = Label(
                    text="No items found for the given Box ID",
                    halign="center",
                    valign="middle",
                    size_hint=(1, 1),
                )
                label.bind(
                    size=lambda *args: label.setter('text_size')(label, label.size)
                )
                centered_message.add_widget(label)
                self.ids.items_results_box.add_widget(centered_message)

        except Exception as e:
            # Display the exception in the UI for debugging
            error_label = Label(
                text=f"Error: {e}",
                halign="center",
                valign="middle",
                size_hint=(1, 1),
                color=(1, 0, 0, 1),  # Red color for error messages
            )
            error_label.bind(
                size=lambda *args: error_label.setter('text_size')(error_label, error_label.size)
            )
            self.ids.items_results_box.add_widget(error_label)
        finally:
            session.close()

    def show_edit_popup(self, item, *args):
        # Create a popup layout for editing
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Fields to edit item details with increased height for better visibility
        location_input = TextInput(text=item.item_location, multiline=False, hint_text="Location", height=40,
                                   size_hint_y=None)
        weight_input = TextInput(text=str(item.item_weight), multiline=False, hint_text="Weight", height=40,
                                 size_hint_y=None)
        description_input = TextInput(text=item.item_description or "", multiline=False, hint_text="Description",
                                      height=40, size_hint_y=None)

        # Add fields to the content
        content.add_widget(Label(text="Edit Item Details", size_hint_y=None, height=30))
        content.add_widget(Label(text="Location", size_hint_y=None, height=20))
        content.add_widget(location_input)
        content.add_widget(Label(text="Weight", size_hint_y=None, height=20))
        content.add_widget(weight_input)
        content.add_widget(Label(text="Description", size_hint_y=None, height=20))
        content.add_widget(description_input)

        # Buttons to save or cancel
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_button = Button(text="Save", size_hint_y=None, height=40,
                             on_press=lambda *args: self.update_item(item, location_input.text, weight_input.text,
                                                                     description_input.text))
        cancel_button = Button(text="Cancel", size_hint_y=None, height=40, on_press=lambda *args: popup.dismiss())

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(button_layout)

        # Popup configuration with increased size
        popup = Popup(title=f"Edit Item ID {item.id}", content=content, size_hint=(0.9, 0.7))
        popup.open()

    def update_item(self, item, location, weight, description):
        # Update item in the database
        session = SessionLocal()
        try:
            # Update item properties
            item.item_location = location
            item.item_weight = float(weight)  # Ensure weight is numeric
            item.item_description = description

            # Commit to the database
            session.merge(item)
            session.commit()
            print(f"Item ID {item.id} updated successfully.")
        except Exception as e:
            print(f"Failed to update item: {e}")
            session.rollback()
        finally:
            session.close()

        # Refresh the item list
        self.find_items_by_box_id()

    def clear_results(self):
        # Clear results
        self.ids.box_id_input.text = ''
        self.ids.items_results_box.clear_widgets()
        self.ids.boxes_with_items_box.clear_widgets()