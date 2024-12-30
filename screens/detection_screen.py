from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/detection_screen.kv")

class DetectionScreen(Screen):
    title = StringProperty('Detection')

    def on_up_pressed(self):
        pass

    def on_down_pressed(self):
        pass