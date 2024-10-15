# src/kivy_app/main.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from src.kivy_app.screens import MainMenuScreen, AddBoxScreen, FindBoxScreen
from src.database import init_db

class BoxApp(App):
    def build(self):
        init_db()

        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(AddBoxScreen(name="add_box"))
        sm.add_widget(FindBoxScreen(name="find_box"))
        return sm

if __name__ == '__main__':
    BoxApp().run()
