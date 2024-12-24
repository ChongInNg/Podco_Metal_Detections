from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/main_screen.kv")

class MainScreen(Screen):
    title = StringProperty("Main Menu")