from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from src.box import Box
from src.boxitem import BoxItem
from src.database import SessionLocal
from src.models import BoxModel, BoxItemModel
from kivy.logger import Logger

class MainMenuScreen(Screen):
    pass

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
                grid.add_widget(Label(text="Box ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))
                grid.add_widget(Label(text="Actions"))

                for box in boxes:
                    grid.add_widget(Label(text=str(box.id)))
                    grid.add_widget(Label(text=box.box_location))
                    grid.add_widget(Label(text=str(box.box_weight)))
                    grid.add_widget(Label(text=box.box_description or ""))

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
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        height_input = TextInput(hint_text="Height", multiline=False)
        length_input = TextInput(hint_text="Length", multiline=False)
        weight_input = TextInput(hint_text="Weight", multiline=False)
        location_input = TextInput(hint_text="Location", multiline=False)
        description_input = TextInput(hint_text="Description", multiline=False)

        content.add_widget(Label(text="Add Box"))
        content.add_widget(height_input)
        content.add_widget(length_input)
        content.add_widget(weight_input)
        content.add_widget(location_input)
        content.add_widget(description_input)

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_button = Button(text="Save")
        save_button.bind(on_press=lambda _: self.add_box(
            height_input.text,
            length_input.text,
            weight_input.text,
            location_input.text,
            description_input.text
        ))
        buttons.add_widget(save_button)

        cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())
        buttons.add_widget(cancel_button)

        content.add_widget(buttons)
        popup = Popup(title="Add Box", content=content, size_hint=(0.8, 0.8))
        popup.open()

    def add_box(self, height, length, weight, location, description):
        Logger.debug("BoxesScreen: add_box() called")
        session = SessionLocal()
        try:
            new_box = BoxModel(
                box_height=float(height),
                box_length=float(length),
                box_weight=float(weight),
                box_location=location,
                box_description=description
            )
            session.add(new_box)
            session.commit()
            Logger.info("BoxesScreen: Box added successfully.")
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to add box - {e}")
            session.rollback()
        finally:
            session.close()
        self.display_boxes()

    def show_edit_popup(self, box):
        Logger.debug(f"BoxesScreen: show_edit_popup() called for Box ID {box.id}")
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        location_input = TextInput(text=box.box_location, multiline=False)
        description_input = TextInput(text=box.box_description, multiline=False)

        content.add_widget(Label(text="Edit Box"))
        content.add_widget(Label(text="Location"))
        content.add_widget(location_input)
        content.add_widget(Label(text="Description"))
        content.add_widget(description_input)

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_button = Button(text="Save")
        save_button.bind(on_press=lambda _: self.edit_box(
            box,
            location_input.text,
            description_input.text
        ))
        buttons.add_widget(save_button)

        cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())
        buttons.add_widget(cancel_button)

        content.add_widget(buttons)
        popup = Popup(title=f"Edit Box ID {box.id}", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def edit_box(self, box, location, description):
        Logger.debug(f"BoxesScreen: edit_box() called for Box ID {box.id}")
        session = SessionLocal()
        try:
            box.box_location = location
            box.box_description = description
            session.merge(box)
            session.commit()
            Logger.info(f"BoxesScreen: Box ID {box.id} updated successfully.")
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to update box - {e}")
            session.rollback()
        finally:
            session.close()
        self.display_boxes()

    def show_delete_popup(self, box):
        Logger.debug(f"BoxesScreen: show_delete_popup() called for Box ID {box.id}")
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Are you sure you want to delete Box ID {box.id}?"))

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        confirm_button = Button(text="Delete", on_press=lambda _: self.delete_box(box))
        cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())

        buttons.add_widget(confirm_button)
        buttons.add_widget(cancel_button)
        content.add_widget(buttons)

        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def delete_box(self, box):
        Logger.debug(f"BoxesScreen: delete_box() called for Box ID {box.id}")
        session = SessionLocal()
        try:
            session.delete(box)
            session.commit()
            Logger.info(f"BoxesScreen: Box ID {box.id} deleted successfully.")
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to delete box - {e}")
            session.rollback()
        finally:
            session.close()
        self.display_boxes()

class BoxItemsScreen(Screen):
    def on_pre_enter(self):
        Logger.debug("BoxItemsScreen: on_pre_enter() called")
        self.clear_results()
        self.display_all_boxes()

    def display_all_boxes(self):
        Logger.debug("BoxItemsScreen: display_all_boxes() called")
        session = SessionLocal()
        self.ids.boxes_with_items_box.clear_widgets()

        try:
            # Retrieve all boxes
            boxes = session.query(BoxModel).all()
            Logger.debug(f"BoxItemsScreen: Found {len(boxes)} total boxes")

            if boxes:
                grid = GridLayout(cols=6, size_hint_y=None, row_default_height=40)  # Increased cols to 6 for spacer
                grid.bind(minimum_height=grid.setter('height'))

                # Header row
                grid.add_widget(Label(text="Box ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))
                grid.add_widget(Label(text=""))  # Spacer column
                grid.add_widget(Label(text="Actions"))

                for box in boxes:
                    # Add Box ID
                    grid.add_widget(Label(text=str(box.id)))
                    # Add Location
                    grid.add_widget(Label(text=box.box_location))
                    # Add Weight
                    grid.add_widget(Label(text=str(box.box_weight)))
                    # Add Description
                    grid.add_widget(Label(text=box.box_description or ""))

                    # Add Spacer
                    grid.add_widget(Label(text=" "))  # Add spacer for better alignment

                    # Add Actions column
                    actions_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_x=None, width=150)

                    # "Edit" button
                    edit_button = Button(
                        text="Edit",
                        size_hint_x=None,
                        width=50,
                        on_press=lambda btn, b=box: self.show_edit_popup(b)
                    )
                    actions_layout.add_widget(edit_button)

                    # "Delete" button
                    delete_button = Button(
                        text="Delete",
                        size_hint_x=None,
                        width=50,
                        background_color=(1, 0, 0, 1),
                        on_press=lambda btn, b=box: self.show_delete_confirmation_popup(b)
                    )
                    actions_layout.add_widget(delete_button)

                    # "Add" button
                    add_button = Button(
                        text="Add",
                        size_hint_x=None,
                        width=50,
                        background_color=(0, 1, 0, 1),  # Green button
                        on_press=lambda btn, b=box: self.show_add_item_popup(b)
                    )
                    actions_layout.add_widget(add_button)

                    grid.add_widget(actions_layout)  # Add the entire actions layout to the grid

                # Scrollable container
                scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
                scrollview.add_widget(grid)
                self.ids.boxes_with_items_box.add_widget(scrollview)
            else:
                self.ids.boxes_with_items_box.add_widget(Label(text="No boxes found."))
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Error displaying boxes - {e}")
        finally:
            session.close()

    def find_items_by_box_id(self):
        Logger.debug("BoxItemsScreen: find_items_by_box_id() called")
        box_id_text = self.ids.box_id_input.text.strip()  # Assuming there’s a TextInput with ID 'box_id_input'
        Logger.debug(f"BoxItemsScreen: Searching items for Box ID '{box_id_text}'")
        session = SessionLocal()

        try:
            self.ids.items_results_box.clear_widgets()  # Assuming there's a BoxLayout with ID 'items_results_box'

            if not box_id_text:
                Logger.warning("BoxItemsScreen: No Box ID entered")
                self.ids.items_results_box.add_widget(Label(text="Please enter a Box ID."))
                return

            try:
                box_id = int(box_id_text)
            except ValueError:
                Logger.error("BoxItemsScreen: Invalid Box ID entered")
                self.ids.items_results_box.add_widget(Label(text="Invalid Box ID. Please enter a valid integer."))
                return

            items = session.query(BoxItemModel).filter_by(box_id=box_id).all()
            Logger.debug(f"BoxItemsScreen: Found {len(items)} items for Box ID {box_id}")

            if items:
                grid = GridLayout(cols=4, size_hint_y=None, row_default_height=30)
                grid.bind(minimum_height=grid.setter('height'))

                # Header row
                grid.add_widget(Label(text="Item ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))

                for item in items:
                    grid.add_widget(Label(text=str(item.id)))
                    grid.add_widget(Label(text=item.item_location))
                    grid.add_widget(Label(text=str(item.item_weight)))
                    grid.add_widget(Label(text=item.item_description or ""))

                scrollview = ScrollView(size_hint=(1, None), height=200)
                scrollview.add_widget(grid)
                self.ids.items_results_box.add_widget(scrollview)
            else:
                self.ids.items_results_box.add_widget(Label(text="No items found for the given Box ID"))
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Error finding items - {e}")
            error_label = Label(
                text=f"Error: {e}",
                halign="center",
                valign="middle",
                size_hint=(1, 1),
                color=(1, 0, 0, 1),
            )
            error_label.bind(size=lambda *args: error_label.setter('text_size')(error_label, error_label.size))
            self.ids.items_results_box.add_widget(error_label)
        finally:
            session.close()

    def add_item_to_box(self, box, height, length, weight, location, description):
        Logger.debug(f"BoxItemsScreen: add_item_to_box() called for Box ID {box.id}")
        session = SessionLocal()
        try:
            new_item = BoxItem(
                box_id=box.id,
                item_height=float(height),
                item_length=float(length),
                item_weight=float(weight),
                item_location=location,
                item_description=description
            )
            new_item.add_item(session)
            Logger.info(f"BoxItemsScreen: Item added to Box ID {box.id} successfully.")
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Failed to add item - {e}")
            session.rollback()
        finally:
            session.close()

        self.display_all_boxes()

    def show_add_item_popup(self, box):
        Logger.debug(f"BoxItemsScreen: show_add_item_popup() called for Box ID {box.id}")
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Input fields for the new item
        height_input = TextInput(multiline=False, hint_text="Height")
        length_input = TextInput(multiline=False, hint_text="Length")
        weight_input = TextInput(multiline=False, hint_text="Weight")
        location_input = TextInput(multiline=False, hint_text="Location")
        description_input = TextInput(multiline=False, hint_text="Description")

        # Add input fields to the popup
        content.add_widget(Label(text="Add Item to Box"))
        content.add_widget(Label(text="Height"))
        content.add_widget(height_input)
        content.add_widget(Label(text="Length"))
        content.add_widget(length_input)
        content.add_widget(Label(text="Weight"))
        content.add_widget(weight_input)
        content.add_widget(Label(text="Location"))
        content.add_widget(location_input)
        content.add_widget(Label(text="Description"))
        content.add_widget(description_input)

        # Add and Cancel buttons
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        add_button = Button(
            text="Add",
            on_press=lambda btn: self.add_item_to_box(
                box,
                height_input.text,
                length_input.text,
                weight_input.text,
                location_input.text,
                description_input.text
            )
        )
        cancel_button = Button(text="Cancel", on_press=lambda btn: popup.dismiss())

        button_layout.add_widget(add_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title=f"Add Item to Box ID {box.id}", content=content, size_hint=(0.8, 0.9))  # Adjusted height
        popup.open()

    def show_edit_popup(self, box):
        Logger.debug(f"BoxItemsScreen: show_edit_popup() called for Box ID {box.id}")
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Input fields for editing
        location_input = TextInput(text=box.box_location, multiline=False, hint_text="Location")
        weight_input = TextInput(text=str(box.box_weight), multiline=False, hint_text="Weight")
        description_input = TextInput(text=box.box_description or "", multiline=False, hint_text="Description")

        # Add inputs to popup
        content.add_widget(Label(text="Edit Box Details"))
        content.add_widget(Label(text="Location"))
        content.add_widget(location_input)
        content.add_widget(Label(text="Weight"))
        content.add_widget(weight_input)
        content.add_widget(Label(text="Description"))
        content.add_widget(description_input)

        # Save and Cancel buttons
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        save_button = Button(
            text="Save",
            on_press=lambda btn: self.update_box(box, location_input.text, weight_input.text, description_input.text)
        )
        cancel_button = Button(text="Cancel", on_press=lambda btn: popup.dismiss())

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title=f"Edit Box ID {box.id}", content=content, size_hint=(0.8, 0.9))  # Adjusted height
        popup.open()

    def show_delete_confirmation_popup(self, box):
        Logger.debug(f"BoxItemsScreen: show_delete_confirmation_popup() called for Box ID {box.id}")
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=f"Are you sure you want to delete Box ID {box.id}?"))

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        delete_button = Button(text="Delete", background_color=(1, 0, 0, 1),
                               on_press=lambda btn: self.delete_box(box))
        cancel_button = Button(text="Cancel", on_press=lambda btn: popup.dismiss())

        button_layout.add_widget(delete_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def show_add_box_popup(self):
        Logger.debug("BoxItemsScreen: show_add_box_popup() called")
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Input fields for adding a new box
        height_input = TextInput(multiline=False, hint_text="Height")
        length_input = TextInput(multiline=False, hint_text="Length")
        weight_input = TextInput(multiline=False, hint_text="Weight")
        location_input = TextInput(multiline=False, hint_text="Location")
        description_input = TextInput(multiline=False, hint_text="Description")

        # Add inputs to popup
        content.add_widget(Label(text="Add New Box"))
        content.add_widget(Label(text="Height"))
        content.add_widget(height_input)
        content.add_widget(Label(text="Length"))
        content.add_widget(length_input)
        content.add_widget(Label(text="Weight"))
        content.add_widget(weight_input)
        content.add_widget(Label(text="Location"))
        content.add_widget(location_input)
        content.add_widget(Label(text="Description"))
        content.add_widget(description_input)

        # Add and Cancel buttons
        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        add_button = Button(text="Add", on_press=lambda btn: self.add_box(height_input.text, length_input.text, weight_input.text, location_input.text, description_input.text))
        cancel_button = Button(text="Cancel", on_press=lambda btn: popup.dismiss())

        button_layout.add_widget(add_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title="Add Box", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def add_box(self, height, length, weight, location, description):
        Logger.debug(f"BoxItemsScreen: add_box() called with height={height}, length={length}, weight={weight}, location={location}, description={description}")
        session = SessionLocal()
        try:
            new_box = BoxModel(
                box_height=float(height),
                box_length=float(length),
                box_weight=float(weight),
                box_location=location,
                box_description=description
            )
            session.add(new_box)
            session.commit()
            Logger.info("BoxItemsScreen: New box added successfully.")
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Failed to add box - {e}")
            session.rollback()
        finally:
            session.close()

        self.display_all_boxes()

    def delete_box(self, box):
        Logger.debug(f"BoxItemsScreen: delete_box() called for Box ID {box.id}")
        session = SessionLocal()
        try:
            session.delete(box)
            session.commit()
            Logger.info(f"BoxItemsScreen: Box ID {box.id} deleted successfully.")
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Failed to delete box - {e}")
            session.rollback()
        finally:
            session.close()

        self.display_all_boxes()

    def clear_results(self):
        Logger.debug("BoxItemsScreen: clear_results() called")
        self.ids.boxes_with_items_box.clear_widgets()