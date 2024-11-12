from kivy.uix.screenmanager import Screen
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
from kivy.logger import Logger

class MainMenuScreen(Screen):
    pass

class AddBoxScreen(Screen):
    def add_box(self):
        box_height = self.ids.box_height.text
        box_length = self.ids.box_length.text
        box_weight = self.ids.box_weight.text
        box_location = self.ids.box_location.text
        box_description = self.ids.box_description.text or "This is a box"

        Logger.debug(f"AddBoxScreen: Adding box with height={box_height}, length={box_length}, weight={box_weight}, location={box_location}, description={box_description}")
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
            Logger.info("AddBoxScreen: Box added successfully.")
        except Exception as e:
            Logger.error(f"AddBoxScreen: Error adding box - {e}")
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
        Logger.debug("FindBoxScreen: find_boxes() called")
        box_location = self.ids.box_location.text
        Logger.debug(f"FindBoxScreen: Searching for boxes at location '{box_location}'")
        session = SessionLocal()
        try:
            results = Box.find_box(session, box_location=box_location)
            Logger.debug(f"FindBoxScreen: Found {len(results)} boxes")
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

                scrollview = ScrollView(size_hint=(1, None), size_hint_y=None, height=300)
                scrollview.add_widget(grid)
                self.ids.results_box.add_widget(scrollview)
            else:
                self.ids.results_box.add_widget(Label(text="No boxes found"))
        except Exception as e:
            Logger.error(f"FindBoxScreen: Error finding boxes - {e}")
        finally:
            session.close()

    def clear_results(self):
        Logger.debug("FindBoxScreen: clear_results() called")
        self.ids.box_location.text = ''
        self.ids.results_box.clear_widgets()

class EditBoxScreen(Screen):
    def edit_box(self):
        Logger.debug("EditBoxScreen: edit_box() called")
        box_id = self.ids.edit_box_id.text
        box_location = self.ids.edit_box_location.text
        box_description = self.ids.edit_box_description.text

        Logger.debug(f"EditBoxScreen: Editing box ID {box_id} with new location '{box_location}' and description '{box_description}'")
        session = SessionLocal()
        try:
            kwargs = {}
            if box_location:
                kwargs['box_location'] = box_location
            if box_description:
                kwargs['box_description'] = box_description

            box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
            box.edit_box(session, box_id=int(box_id), **kwargs)
            Logger.info(f"EditBoxScreen: Box ID {box_id} edited successfully.")
        except Exception as e:
            Logger.error(f"EditBoxScreen: Error editing box - {e}")
        finally:
            session.close()

    def clear_inputs(self):
        Logger.debug("EditBoxScreen: clear_inputs() called")
        self.ids.edit_box_id.text = ''
        self.ids.edit_box_location.text = ''
        self.ids.edit_box_description.text = ''

class DeleteBoxScreen(Screen):
    def show_confirm_button(self):
        Logger.debug("DeleteBoxScreen: show_confirm_button() called")
        self.ids.confirm_delete_button.opacity = 1
        self.ids.confirm_delete_button.disabled = False

    def delete_box(self):
        Logger.debug("DeleteBoxScreen: delete_box() called")
        box_id = self.ids.delete_box_id.text

        if not box_id.isdigit():
            Logger.error("DeleteBoxScreen: Invalid Box ID entered")
            return

        session = SessionLocal()
        try:
            box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
            box.delete_box(session, box_id=int(box_id))
            Logger.info(f"DeleteBoxScreen: Box ID {box_id} deleted successfully.")
        except Exception as e:
            Logger.error(f"DeleteBoxScreen: Error deleting box - {e}")
        finally:
            session.close()
            self.clear_inputs()

    def clear_inputs(self):
        Logger.debug("DeleteBoxScreen: clear_inputs() called")
        self.ids.delete_box_id.text = ''
        self.ids.confirm_delete_button.opacity = 0
        self.ids.confirm_delete_button.disabled = True

class BoxItemsScreen(Screen):
    def on_pre_enter(self):
        Logger.debug("BoxItemsScreen: on_pre_enter() called")
        self.clear_results()
        self.display_boxes_with_items()

    def display_boxes_with_items(self):
        Logger.debug("BoxItemsScreen: display_boxes_with_items() called")
        session = SessionLocal()
        self.ids.boxes_with_items_box.clear_widgets()

        try:
            boxes_with_items = (
                session.query(BoxModel)
                .join(BoxItemModel, BoxModel.id == BoxItemModel.box_id)
                .distinct()
                .all()
            )
            Logger.debug(f"BoxItemsScreen: Found {len(boxes_with_items)} boxes with items")

            if boxes_with_items:
                grid = GridLayout(cols=5, size_hint_y=None, row_default_height=40)
                grid.bind(minimum_height=grid.setter('height'))

                grid.add_widget(Label(text="", size_hint_x=None, width=30))
                grid.add_widget(Label(text="Box ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))

                for box in boxes_with_items:
                    add_item_label = Label(
                        text="[color=#0000FF][u]Add Item[/u][/color]",
                        markup=True,
                        size_hint_x=None,
                        width=50,
                        height=30
                    )
                    # Corrected the binding to capture the current box
                    add_item_label.bind(
                        on_touch_down=lambda lbl, touch, b=box: self.show_add_item_popup(b)
                        if lbl.collide_point(*touch.pos) else None
                    )

                    grid.add_widget(add_item_label)
                    grid.add_widget(Label(text=str(box.id)))
                    grid.add_widget(Label(text=box.box_location))
                    grid.add_widget(Label(text=str(box.box_weight)))
                    grid.add_widget(Label(text=box.box_description or ""))

                scrollview = ScrollView(size_hint=(1, None), size_hint_y=None, height=200)
                scrollview.add_widget(grid)
                self.ids.boxes_with_items_box.add_widget(scrollview)
            else:
                self.ids.boxes_with_items_box.add_widget(Label(text="No boxes with items found."))
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Error displaying boxes with items - {e}")
        finally:
            session.close()

    def add_item_to_box(self, box, location, weight, description):
        Logger.debug(f"BoxItemsScreen: add_item_to_box() called for Box ID {box.id}")
        session = SessionLocal()
        try:
            new_item = BoxItemModel(
                box_id=box.id,
                item_location=location,
                item_weight=float(weight),
                item_description=description
            )
            session.add(new_item)
            session.commit()
            Logger.info(f"BoxItemsScreen: Item added to Box ID {box.id} successfully.")
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Failed to add item - {e}")
            session.rollback()
        finally:
            session.close()

        self.display_boxes_with_items()

    def show_add_item_popup(self, box):
        Logger.debug(f"BoxItemsScreen: show_add_item_popup() called for Box ID {box.id}")
        # ... (rest of the method remains the same)

    def find_items_by_box_id(self):
        Logger.debug("BoxItemsScreen: find_items_by_box_id() called")
        box_id_text = self.ids.box_id_input.text.strip()
        Logger.debug(f"BoxItemsScreen: Searching items for Box ID '{box_id_text}'")
        session = SessionLocal()

        try:
            self.ids.items_results_box.clear_widgets()

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
                grid = GridLayout(cols=5, size_hint_y=None, row_default_height=30)
                grid.bind(minimum_height=grid.setter('height'))

                grid.add_widget(Label(text="", size_hint_x=None, width=20))
                grid.add_widget(Label(text="Item ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))

                for item in items:
                    edit_label = Label(
                        text="[color=#0000FF][u]Edit[/u][/color]",
                        markup=True,
                        size_hint_x=None,
                        width=20,
                        height=30
                    )
                    # Corrected the binding to capture the current item
                    edit_label.bind(on_touch_down=lambda lbl, touch, i=item: self.show_edit_popup(i)
                                    if lbl.collide_point(*touch.pos) else None)

                    grid.add_widget(edit_label)
                    grid.add_widget(Label(text=str(item.id)))
                    grid.add_widget(Label(text=item.item_location))
                    grid.add_widget(Label(text=str(item.item_weight)))
                    grid.add_widget(Label(text=item.item_description or ""))

                scrollview = ScrollView(size_hint=(1, None), size_hint_y=None, height=300)
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
            error_label.bind(
                size=lambda *args: error_label.setter('text_size')(error_label, error_label.size)
            )
            self.ids.items_results_box.add_widget(error_label)
        finally:
            session.close()

    def show_edit_popup(self, item, *args):
        Logger.debug(f"BoxItemsScreen: show_edit_popup() called for Item ID {item.id}")
        # ... (rest of the method remains the same)

    def update_item(self, item, location, weight, description):
        Logger.debug(f"BoxItemsScreen: update_item() called for Item ID {item.id}")
        session = SessionLocal()
        try:
            item.item_location = location
            item.item_weight = float(weight)
            item.item_description = description

            session.merge(item)
            session.commit()
            Logger.info(f"BoxItemsScreen: Item ID {item.id} updated successfully.")
        except Exception as e:
            Logger.error(f"BoxItemsScreen: Failed to update item - {e}")
            session.rollback()
        finally:
            session.close()

        self.find_items_by_box_id()

    def clear_results(self):
        Logger.debug("BoxItemsScreen: clear_results() called")
        self.ids.box_id_input.text = ''
        self.ids.items_results_box.clear_widgets()
        self.ids.boxes_with_items_box.clear_widgets()