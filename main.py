# src/kivy_app/main.py
import kivy
kivy.logger.Logger.setLevel("DEBUG")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from src.kivy_app.screens import MainMenuScreen, AddBoxScreen, FindBoxScreen, EditBoxScreen, DeleteBoxScreen, BoxItemsScreen
from src.database import init_db

class BoxApp(App):
    def build(self):
        init_db()

        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(AddBoxScreen(name="add_box"))
        sm.add_widget(FindBoxScreen(name="find_box"))
        sm.add_widget(EditBoxScreen(name="edit_box"))
        sm.add_widget(DeleteBoxScreen(name="delete_box"))
        sm.add_widget(BoxItemsScreen(name="box_items"))
        return sm

if __name__ == '__main__':
    BoxApp().run()