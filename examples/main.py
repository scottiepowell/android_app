import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import logging
import random

kivy.require('2.3.0')

class MyRoot(BoxLayout):

    def __init__(self, **kwargs):
        super(MyRoot, self).__init__(**kwargs)

    def generate_number(self):
        self.ids.random_label.text = str(random.randint(0,1000))
        return MyRoot()

class NeuralRandom(App):

    def build(self):
        return MyRoot()

    def print_size(self, instance):
        logging.debug(f"Widget {instance} size: {instance.size}")

    def print_pos(self, instance):
        logging.debug(f"Widget {instance} position: {instance.pos}")

    def debug_press(self):
        logging.debug("Button pressed")

neuralRandom = NeuralRandom()
neuralRandom.run()


