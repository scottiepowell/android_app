from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import os

class CameraHandler(BoxLayout):
    def __init__(self, save_directory, on_picture_taken_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.save_directory = save_directory
        self.on_picture_taken_callback = on_picture_taken_callback
        self.camera = Camera(play=True, resolution=(640, 480))
        self.add_widget(self.camera)

        # Capture button
        capture_button = Button(text="Capture", size_hint_y=0.1)
        capture_button.bind(on_press=self.capture_picture)
        self.add_widget(capture_button)

    def capture_picture(self, *args):
        """Capture the picture and save to file."""
        filename = os.path.join(self.save_directory, "captured_image.jpg")
        self.camera.export_to_png(filename)
        self.on_picture_taken_callback(filename)
        self.parent.dismiss()

    @staticmethod
    def show_camera_popup(save_directory, on_picture_taken_callback):
        """Show the camera in a popup for taking pictures."""
        content = CameraHandler(save_directory, on_picture_taken_callback)
        popup = Popup(title="Take Picture", content=content, size_hint=(0.9, 0.9))
        content.parent = popup
        popup.open()
