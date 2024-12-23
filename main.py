# main.py
import kivy
kivy.logger.Logger.setLevel("DEBUG")

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from src.kivy_app.screens.main_menu_screen import MainMenuScreen
from src.kivy_app.screens.boxes_screen import BoxesScreen
from src.kivy_app.screens.box_items_screen import BoxItemsScreen
from src.kivy_app.screens.boxes_screen_display_boxes import BoxesScreenDisplayBoxes
from src.database import init_db

Builder.load_file("src/kivy_app/box.kv")

class BoxApp(App):
    def build(self):
        Logger.debug("BoxApp: Initializing database...")
        init_db()

        Logger.debug("BoxApp: Setting up ScreenManager with all screens...")
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(BoxesScreen(name="boxes"))
        sm.add_widget(BoxItemsScreen(name="box_items"))
        sm.add_widget(BoxesScreenDisplayBoxes())
        return sm

if __name__ == '__main__':
    Logger.debug("BoxApp: Starting app...")
    BoxApp().run()
