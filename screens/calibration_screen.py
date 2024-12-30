from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/calibration_screen.kv")

class CalibrationScreen(Screen):
    title = StringProperty('Calibration')
    current_T = StringProperty("0")
    current_D = StringProperty("0")
    current_CH1_P = StringProperty("0")
    current_CH1_N = StringProperty("0")
    current_CH1_M = StringProperty("0")
    current_CH2_P = StringProperty("0")
    current_CH2_N = StringProperty("0")
    current_CH2_M = StringProperty("0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_T = "100.1"
        self.current_D = "1234"
        self.current_CH1_P = "1234"
        self.current_CH1_N = "1234"
        self.current_CH1_M = "1234"

        self.current_CH2_P = "4321"
        self.current_CH2_N = "4321"
        self.current_CH2_M = "4321"