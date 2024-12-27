from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
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

    # Dropdown or toggle for Add Picture options
    add_picture_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
    add_picture_label = Label(text="Add Picture:", size_hint_x=0.4)
    add_picture_button_camera = Button(text="Use Camera", size_hint_x=0.3)
    add_picture_button_filechooser = Button(text="Choose File", size_hint_x=0.3)

    add_picture_layout.add_widget(add_picture_label)
    add_picture_layout.add_widget(add_picture_button_camera)
    add_picture_layout.add_widget(add_picture_button_filechooser)
    popup_layout.add_widget(add_picture_layout)

    image_thumbnail = Image(size_hint=(1, None), height=100, allow_stretch=True, keep_ratio=True)
    popup_layout.add_widget(image_thumbnail)

    # Open camera logic
    def open_camera(instance):
        save_directory = os.path.join(os.getcwd(), "images")
        os.makedirs(save_directory, exist_ok=True)

        def on_picture_taken(image_path):
            # Load and process the captured image
            try:
                image_data = ImageHandler.load_image(image_path)
                thumbnail_data["data"] = ImageHandler.create_thumbnail(image_data)
                image_thumbnail.texture = ImageHandler.bytes_to_texture(thumbnail_data["data"])
            except Exception as e:
                Logger.error(f"Failed to process captured image: {e}")

        CameraHandler.show_camera_popup(save_directory, on_picture_taken)

    add_picture_button_camera.bind(on_press=open_camera)

    # Open file chooser logic
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
                    image_thumbnail.texture = ImageHandler.bytes_to_texture(thumbnail_data["data"])
                except Exception as e:
                    Logger.error(f"Failed to load image: {e}")

                filechooser_popup.dismiss()

        filechooser_buttons = BoxLayout(size_hint=(1, 0.1), spacing=10)
        confirm_button = Button(text="Select", on_press=show_image_preview)
        cancel_button = Button(text="Cancel", on_press=lambda _: filechooser_popup.dismiss())
        filechooser_buttons.add_widget(confirm_button)
        filechooser_buttons.add_widget(cancel_button)

        filechooser_layout.add_widget(filechooser_buttons)
        filechooser_popup.content = filechooser_layout
        filechooser_popup.open()

    add_picture_button_filechooser.bind(on_press=open_filechooser)

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
                cancel_button = Button(text="Return", on_press=cancel_image)
                preview_buttons.add_widget(save_button)
                preview_buttons.add_widget(cancel_button)

                preview_layout.add_widget(preview_buttons)
                preview_popup.content = preview_layout
                preview_popup.open()

        filechooser_buttons = BoxLayout(size_hint=(1, 0.1), spacing=10)
        confirm_button = Button(text="Select", on_press=show_image_preview)
        cancel_button = Button(text="Return", on_press=lambda _: filechooser_popup.dismiss())
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
            #screen.display_boxes()
            screen.on_pre_enter()
        except Exception as e:
            Logger.error(f"BoxesScreen: Failed to update box - {e}")
            session.rollback()
        finally:
            session.close()
        popup.dismiss()

    save_button = Button(text="Save", on_press=save_changes)
    button_layout.add_widget(save_button)

    cancel_button = Button(text="Return", on_press=lambda _: popup.dismiss())
    button_layout.add_widget(cancel_button)

    popup_layout.add_widget(button_layout)
    popup = Popup(title=f"Edit Box {box.alias}", content=popup_layout, size_hint=(0.8, 0.8))
    popup.open()

def show_view_popup(box, boxes, current_index, screen):
    Logger.debug(f"BoxesScreen: show_view_popup() called for Alias {box.alias}")

    # Navigation logic
    def navigate_box(direction):
        new_index = current_index + direction
        if 0 <= new_index < len(boxes):
            popup.dismiss()
            show_view_popup(boxes[new_index], boxes, new_index, screen)

    # Main popup layout
    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    # ScrollView for vertical scrolling
    scroll_view = ScrollView(size_hint=(1, 1))
    content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
    content_layout.bind(minimum_height=content_layout.setter('height'))

    # 1. Display the picture at the top
    if box.box_picture:
        try:
            picture_data = box.box_picture
            picture_texture = ImageHandler.bytes_to_texture(picture_data)
            picture = Image(texture=picture_texture, size_hint=(1, None), height=400, allow_stretch=True,
                            keep_ratio=True)
        except Exception as e:
            Logger.error(f"Failed to load picture for box {box.alias}: {e}")
            picture_texture = None
    else:
        # Use a placeholder full-sized image if no picture is available
        try:
            default_image_data = ImageHandler.resolve_asset("assets/na.jpeg")
            resized_default_data = ImageHandler.resize_default_thumbnail(default_image_data, size=(400, 400))
            picture_texture = ImageHandler.bytes_to_texture(resized_default_data)
        except Exception as e:
            Logger.error(f"Failed to load default placeholder image: {e}")
            picture_texture = None

    if picture_texture:
        picture = Image(texture=picture_texture, size_hint=(1, None), height=400, allow_stretch=True, keep_ratio=True)
        content_layout.add_widget(picture)
    else:
        content_layout.add_widget(Label(text="Picture Unavailable", size_hint_y=None, height=400))

    # 2. Add fields in a GridLayout (3 fields per row)
    grid = GridLayout(cols=3, spacing=10, size_hint_y=None, row_default_height=100)
    grid.bind(minimum_height=grid.setter('height'))

    fields = {
        "Alias": box.alias,
        "Description": box.box_description,
        "Location": box.box_location,
        "Height": f"{box.box_height} units" if box.box_height else "N/A",
        "Weight": f"{box.box_weight} units" if box.box_weight else "N/A",
        "Length": f"{box.box_length} units" if box.box_length else "N/A",
        "User Tags": box.box_user_defined_tags or "N/A"
    }

    for field_name, field_value in fields.items():
        field_label = Label(
            text=f"[b]{field_name}:[/b] {field_value}",
            markup=True,
            halign="left",
            valign="middle",
            size_hint_x=1,  # Stretch labels evenly
            size_hint_y=None,
            text_size=(None, None)  # Prevent truncation
        )
        field_label.bind(size=lambda label, size: setattr(label, "text_size", (label.width - 20, None)))
        grid.add_widget(field_label)

    content_layout.add_widget(grid)

    # 3. Navigation buttons (Previous, Next, and Return)
    nav_buttons_layout = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[10, 0])

    prev_button = Button(text="Previous", size_hint=(0.3, None), height=40)
    prev_button.bind(on_press=lambda _: navigate_box(-1))
    prev_button.disabled = current_index == 0
    nav_buttons_layout.add_widget(prev_button)

    return_button = Button(text="Return", size_hint=(0.3, None), height=40)
    return_button.bind(on_press=lambda _: popup.dismiss())
    nav_buttons_layout.add_widget(return_button)

    next_button = Button(text="Next", size_hint=(0.3, None), height=40)
    next_button.bind(on_press=lambda _: navigate_box(1))
    next_button.disabled = current_index == len(boxes) - 1
    nav_buttons_layout.add_widget(next_button)

    # Combine everything into the popup
    scroll_view.add_widget(content_layout)
    popup_layout.add_widget(scroll_view)
    popup_layout.add_widget(nav_buttons_layout)

    popup = Popup(title=f"View Box: {box.alias}", content=popup_layout, size_hint=(0.9, 0.9))
    popup.open()

def show_alias_edit_popup(parent_screen, db_box, box_theme):
    """Shows a popup to edit the alias of the given box."""
    Logger.debug(f"show_alias_edit_popup: Called for Box ID {db_box.id}")

    # Popup content
    content = BoxLayout(orientation="vertical", spacing=10, padding=10)
    alias_input = TextInput(text=db_box.alias if db_box.alias else "", multiline=False, hint_text="Enter new alias")

    # Buttons
    button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
    save_button = Button(
        text="Save",
        on_press=lambda btn: save_alias(parent_screen, db_box, alias_input.text),
    )
    cancel_button = Button(text="Return", on_press=lambda btn: popup.dismiss())

    button_layout.add_widget(save_button)
    button_layout.add_widget(cancel_button)

    # Add widgets to content
    content.add_widget(Label(text="Edit Alias", size_hint_y=None, height=30))
    content.add_widget(alias_input)
    content.add_widget(button_layout)

    # Create and open the popup
    popup = Popup(title="Edit Alias", content=content, size_hint=(0.7, 0.5))
    popup.open()


def save_alias(parent_screen, db_box, new_alias):
    """Saves the new alias to the database and handles duplicate alias errors."""
    Logger.debug(f"save_alias: Called for Box ID {db_box.id} with new alias '{new_alias}'")

    # Update alias in the database
    session = SessionLocal()
    try:
        existing_box = session.query(BoxModel).filter_by(alias=new_alias).first()
        if existing_box:
            Logger.error(f"Alias '{new_alias}' already exists for Box ID {existing_box.id}.")

            # Generate suggestions using the alias utilities
            alias_dict = parent_screen.alias_dict  # Preloaded alias dictionary
            theme = parent_screen.current_theme or "default"
            suggestions = []

            try:
                for _ in range(3):
                    suggestion = generate_unique_alias(session, BoxModel, theme, alias_dict, is_box=True)
                    if suggestion not in suggestions:  # Avoid duplicates in suggestions
                        suggestions.append(suggestion)
            except ValueError as e:
                Logger.error(f"Error generating alias suggestions: {e}")

            if not suggestions:
                suggestions = [f"{new_alias}_1", f"{new_alias}_2", f"{new_alias}_3"]
                Logger.debug(f"Fallback suggestions generated: {suggestions}")

            show_duplicate_alias_popup(parent_screen, db_box, new_alias, suggestions)
            return

        box = session.query(BoxModel).filter_by(id=db_box.id).first()
        if not box:
            Logger.error(f"Box with ID {db_box.id} not found. Cannot update alias.")
            return
        box.alias = new_alias
        session.commit()
        Logger.info(f"Alias for Box ID {db_box.id} updated to '{new_alias}'.")

        # Refresh the display on the parent screen
        parent_screen.on_pre_enter()
    except Exception as e:
        Logger.error(f"Error updating alias for Box ID {db_box.id}: {e}")
        session.rollback()
    finally:
        session.close()

def show_duplicate_alias_popup(parent_screen, db_box, attempted_alias, suggestions):
    """Show a popup when a duplicate alias is detected."""
    Logger.debug(f"show_duplicate_alias_popup: Called for Box ID {db_box.id} with alias '{attempted_alias}'")

    # Popup content
    content = BoxLayout(orientation="vertical", spacing=10, padding=10)
    content.add_widget(Label(text=f"The alias '{attempted_alias}' already exists.", size_hint_y=None, height=30))

    if suggestions:
        content.add_widget(Label(text="Here are some suggestions:", size_hint_y=None, height=20))
        for suggestion in suggestions:
            content.add_widget(Label(text=f"• {suggestion}", size_hint_y=None, height=20))
    else:
        content.add_widget(Label(text="No suggestions available.", size_hint_y=None, height=30))

    # Buttons
    button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
    close_button = Button(text="Close", on_press=lambda btn: popup.dismiss())
    button_layout.add_widget(close_button)
    content.add_widget(button_layout)

    # Create and open the popup
    popup = Popup(title="Duplicate Alias", content=content, size_hint=(0.7, 0.5))
    popup.open()