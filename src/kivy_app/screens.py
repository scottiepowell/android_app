from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from src.box import Box
from src.database import SessionLocal

class MainMenuScreen(Screen):
    pass

class AddBoxScreen(Screen):
    def add_box(self):
        # Retrieve user input
        box_height = self.ids.box_height.text
        box_length = self.ids.box_length.text
        box_weight = self.ids.box_weight.text
        box_location = self.ids.box_location.text
        box_description = self.ids.box_description.text

        if not box_description:
            box_description = "This is a box"

        # Call the Box class logic to add the box to the database
        session = SessionLocal()
        try:
            box = Box(
                box_height=float(box_height),
                box_length=float(box_length),
                box_weight=float(box_weight),
                box_location=box_location,
                box_description=box_description,
                box_picture=None,
                box_user_defined_tags=None
            )
            box.add_box(session)
            # Optionally show confirmation message
            print("Box added successfully")
        finally:
            session.close()

    def clear_inputs(self):
        # Clear the input fields in the AddBoxScreen
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
            if results:
                self.ids.results_box.clear_widgets()

                # Create a GridLayout to display results in tabular format
                grid = GridLayout(cols=4, size_hint_y=None, row_default_height=40)
                grid.bind(minimum_height=grid.setter('height'))

                # Add header row
                grid.add_widget(Label(text="Box ID"))
                grid.add_widget(Label(text="Location"))
                grid.add_widget(Label(text="Weight"))
                grid.add_widget(Label(text="Description"))

                # Add each box's details in rows
                for box in results:
                    grid.add_widget(Label(text=str(box.id)))
                    grid.add_widget(Label(text=box.box_location))
                    grid.add_widget(Label(text=str(box.box_weight)))
                    grid.add_widget(Label(text=box.box_description))

                # Add the GridLayout to a ScrollView
                scrollview = ScrollView(size_hint=(1, None), size=(self.width, 300))
                scrollview.add_widget(grid)

                # Add the ScrollView to the results box layout
                self.ids.results_box.add_widget(scrollview)
            else:
                self.ids.results_box.clear_widgets()
                self.ids.results_box.add_widget(Label(text="No boxes found"))
        finally:
            session.close()

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

    def delete_box(self):
        box_id = self.ids.delete_box_id.text
        session = SessionLocal()
        try:
            box = Box(box_height=None, box_length=None, box_weight=None, box_location=None)
            box.delete_box(session, box_id=int(box_id))
            print(f"Box ID: {box_id} deleted successfully.")
        finally:
            session.close()

    def clear_results(self):
        self.ids.box_location.text = ''
        self.ids.results_box.clear_widgets()

    def clear_results(self):
        # Clear the input and output fields in the FindBoxScreen
        self.ids.box_location.text = ''
        self.ids.results_box.clear_widgets()