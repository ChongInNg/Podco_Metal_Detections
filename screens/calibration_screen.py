from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/calibration_screen.kv")

class CalibrationScreen(Screen):
    title = StringProperty('Calibration')
