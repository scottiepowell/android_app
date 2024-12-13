from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.logger import Logger
from src.image import ImageHandler
from src.utils.alias_utils import load_aliases, generate_unique_alias
from src.models import BoxModel
from src.database import SessionLocal

def show_add_box_popup(screen):
    Logger.debug("BoxesScreen: show_add_box_popup() called")

    selected_image_path = {"path": None}
    thumbnail_data = {"data": None}

    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    # Description and Location inputs
    basic_fields_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
    description_input = TextInput(hint_text="Description", multiline=False, size_hint_x=0.8)
    location_input = TextInput(hint_text="Location", multiline=False, size_hint_x=0.2)
    basic_fields_layout.add_widget(description_input)
    basic_fields_layout.add_widget(location_input)
    popup_layout.add_widget(Label(text="Description and Location"))
    popup_layout.add_widget(basic_fields_layout)

    # Add Picture Button
    add_picture_button = Button(text="Add Picture", size_hint_y=None, height=40)
    image_thumbnail = Image(size_hint=(1, None), height=100, allow_stretch=True, keep_ratio=True)
    popup_layout.add_widget(add_picture_button)

    def open_filechooser(instance):
        filechooser_popup = Popup(title="Choose Image", size_hint=(0.9, 0.9))
        filechooser_layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(filters=["*.jpg", "*.jpeg"], size_hint=(1, 0.9))
        filechooser_layout.add_widget(filechooser)

        def show_image_preview(instance):
            selected = filechooser.selection
            if selected:
                selected_image_path["path"] = selected[0]
                try:
                    image_data = ImageHandler.load_image(selected[0])
                    thumbnail_data["data"] = ImageHandler.create_thumbnail(image_data)
                except Exception as e:
                    Logger.error(f"Failed to load image: {e}")
                    return

                preview_popup = Popup(title="Preview Image", size_hint=(0.9, 0.9))
                preview_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
                full_image = Image(size_hint=(1, None), height=400, allow_stretch=True, keep_ratio=True)
                full_image.texture = ImageHandler.bytes_to_texture(image_data)
                preview_layout.add_widget(full_image)

                def confirm_image(instance):
                    image_thumbnail.texture = ImageHandler.bytes_to_texture(thumbnail_data["data"])
                    add_picture_button.opacity = 0
                    popup_layout.remove_widget(add_picture_button)
                    popup_layout.add_widget(image_thumbnail, index=1)
                    preview_popup.dismiss()
                    filechooser_popup.dismiss()

                def cancel_image(instance):
                    selected_image_path["path"] = None
                    preview_popup.dismiss()

                preview_buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
                save_button = Button(text="Save", on_press=confirm_image)
                cancel_button = Button(text="Cancel", on_press=cancel_image)
                preview_buttons.add_widget(save_button)
                preview_buttons.add_widget(cancel_button)

                preview_layout.add_widget(preview_buttons)
                preview_popup.content = preview_layout
                preview_popup.open()

        filechooser_buttons = BoxLayout(size_hint=(1, 0.1), spacing=10)
        confirm_button = Button(text="Select", on_press=show_image_preview)
        cancel_button = Button(text="Cancel", on_press=lambda _: filechooser_popup.dismiss())
        filechooser_buttons.add_widget(confirm_button)
        filechooser_buttons.add_widget(cancel_button)

        filechooser_layout.add_widget(filechooser_buttons)
        filechooser_popup.content = filechooser_layout
        filechooser_popup.open()

    add_picture_button.bind(on_press=open_filechooser)

    # Buttons for save/cancel
    button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
    save_button = Button(text="Save")

    def save_box_and_image(instance):
        session = SessionLocal()
        try:
            alias_dict = load_aliases()
            theme = "animals"
            alias = generate_unique_alias(session, BoxModel, theme, alias_dict, is_box=True)

            new_box = BoxModel(
                alias=alias,
                box_description=description_input.text,
                box_location=location_input.text
            )
            session.add(new_box)
            session.commit()

            if selected_image_path["path"]:
                image_data = ImageHandler.load_image(selected_image_path["path"])
                box = session.query(BoxModel).filter_by(alias=alias).first()
                ImageHandler.save_to_database(session, box, 'box_picture', image_data)
                if thumbnail_data["data"]:
                    ImageHandler.save_to_database(session, box, 'box_thumbnail', thumbnail_data["data"])

            Logger.info(f"BoxesScreen: Box added successfully with alias '{alias}'")
            screen.display_boxes()
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to add box - {e}")
            session.rollback()
        finally:
            session.close()

    save_button.bind(on_press=save_box_and_image)
    button_layout.add_widget(save_button)

    cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())
    button_layout.add_widget(cancel_button)

    popup_layout.add_widget(button_layout)
    popup = Popup(title="Add Box", content=popup_layout, size_hint=(0.8, 0.8))
    popup.open()

def show_delete_popup(screen, box):
    Logger.debug(f"BoxesScreen: show_delete_popup() called for Alias {box.alias}")

    # Confirmation popup layout
    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
    popup_layout.add_widget(Label(text=f"Are you sure you want to delete the box '{box.alias}'?"))

    # Buttons for Yes/No
    button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

    def confirm_delete(instance):
        screen.delete_box(box)  # Call delete_box method from BoxesScreen
        popup.dismiss()         # Close popup after deletion

    yes_button = Button(text="Yes", on_press=confirm_delete)
    button_layout.add_widget(yes_button)

    no_button = Button(text="No", on_press=lambda _: popup.dismiss())
    button_layout.add_widget(no_button)

    popup_layout.add_widget(button_layout)

    # Create and display popup
    popup = Popup(title="Confirm Delete", content=popup_layout, size_hint=(0.6, 0.4))
    popup.open()

def show_edit_popup(screen, box):
    Logger.debug(f"BoxesScreen: show_edit_popup() called for Alias {box.alias}")

    # Main popup layout
    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    # Description and Location inputs
    basic_fields_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
    description_input = TextInput(text=box.box_description, multiline=False, size_hint_x=0.8)
    location_input = TextInput(text=box.box_location, multiline=False, size_hint_x=0.2)
    basic_fields_layout.add_widget(description_input)
    basic_fields_layout.add_widget(location_input)
    popup_layout.add_widget(Label(text="Description and Location"))
    popup_layout.add_widget(basic_fields_layout)

    # Display existing picture (if any) and add "Edit Picture" button
    image_thumbnail = Image(size_hint=(1, None), height=100, allow_stretch=True, keep_ratio=True)
    if box.box_thumbnail:
        image_thumbnail.texture = ImageHandler.bytes_to_texture(box.box_thumbnail)
    popup_layout.add_widget(image_thumbnail)

    edit_picture_button = Button(text="Edit Picture", size_hint_y=None, height=40)
    popup_layout.add_widget(edit_picture_button)

    selected_image_path = {"path": None}
    thumbnail_data = {"data": None}

    def open_filechooser(instance):
        filechooser_popup = Popup(title="Choose Image", size_hint=(0.9, 0.9))
        filechooser_layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(filters=["*.jpg", "*.jpeg"], size_hint=(1, 0.9))
        filechooser_layout.add_widget(filechooser)

        def show_image_preview(instance):
            selected = filechooser.selection
            if selected:
                selected_image_path["path"] = selected[0]
                try:
                    image_data = ImageHandler.load_image(selected[0])
                    thumbnail_data["data"] = ImageHandler.create_thumbnail(image_data)
                except Exception as e:
                    Logger.error(f"Failed to load image: {e}")
                    return

                preview_popup = Popup(title="Preview Image", size_hint=(0.9, 0.9))
                preview_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
                full_image = Image(size_hint=(1, None), height=400, allow_stretch=True, keep_ratio=True)
                full_image.texture = ImageHandler.bytes_to_texture(image_data)
                preview_layout.add_widget(full_image)

                def confirm_image(instance):
                    image_thumbnail.texture = ImageHandler.bytes_to_texture(thumbnail_data["data"])
                    preview_popup.dismiss()
                    filechooser_popup.dismiss()

                def cancel_image(instance):
                    selected_image_path["path"] = None
                    preview_popup.dismiss()

                preview_buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
                save_button = Button(text="Save", on_press=confirm_image)
                cancel_button = Button(text="Cancel", on_press=cancel_image)
                preview_buttons.add_widget(save_button)
                preview_buttons.add_widget(cancel_button)

                preview_layout.add_widget(preview_buttons)
                preview_popup.content = preview_layout
                preview_popup.open()

        filechooser_buttons = BoxLayout(size_hint=(1, 0.1), spacing=10)
        confirm_button = Button(text="Select", on_press=show_image_preview)
        cancel_button = Button(text="Cancel", on_press=lambda _: filechooser_popup.dismiss())
        filechooser_buttons.add_widget(confirm_button)
        filechooser_buttons.add_widget(cancel_button)

        filechooser_layout.add_widget(filechooser_buttons)
        filechooser_popup.content = filechooser_layout
        filechooser_popup.open()

    edit_picture_button.bind(on_press=open_filechooser)

    # Additional fields
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

    popup_layout.add_widget(additional_fields_layout)

    # Save and Cancel Buttons
    button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

    def save_changes(instance):
        session = SessionLocal()
        try:
            # Update box fields
            box.box_description = description_input.text
            box.box_location = location_input.text
            box.box_height = float(height_input.text) if height_input.text else None
            box.box_length = float(length_input.text) if length_input.text else None
            box.box_weight = float(weight_input.text) if weight_input.text else None

            # Update image if edited
            if selected_image_path["path"]:
                image_data = ImageHandler.load_image(selected_image_path["path"])
                box.box_picture = image_data
                if thumbnail_data["data"]:
                    box.box_thumbnail = thumbnail_data["data"]

            session.merge(box)
            session.commit()
            Logger.info(f"BoxesScreen: Box with alias {box.alias} updated successfully.")
            screen.display_boxes()
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to update box - {e}")
            session.rollback()
        finally:
            session.close()
        popup.dismiss()

    save_button = Button(text="Save", on_press=save_changes)
    button_layout.add_widget(save_button)

    cancel_button = Button(text="Cancel", on_press=lambda _: popup.dismiss())
    button_layout.add_widget(cancel_button)

    popup_layout.add_widget(button_layout)
    popup = Popup(title=f"Edit Box {box.alias}", content=popup_layout, size_hint=(0.8, 0.8))
    popup.open()