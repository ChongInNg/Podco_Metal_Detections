from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from .stack_widget import StackWidget

Builder.load_file("kv/main_screen.kv")

class MainScreen(Screen):
    title = StringProperty("Main Menu")

    def get_stack_widget(self)->StackWidget:
        return self.ids.stack_widget