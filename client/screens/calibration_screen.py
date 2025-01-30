from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from dataclasses import dataclass

Builder.load_file("kv/calibration_screen.kv")

@dataclass
class CalibrationData:
    T_Value: str
    D_Value: str
    CH1_P: str
    CH1_N: str
    CH1_M: str
    CH2_P: str
    CH2_N: str
    CH2_M: str

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

    def on_kv_post(self, base_widget):
       pass

    def reset_data(self):
        pass # no need reset when changing the data

    def get_title(self):
        return self.title
    
    def update_data(self, data: CalibrationData) -> None:
        print("Updating data...")
        self.current_T = data.T_Value
        self.current_D = data.D_Value
        self.current_CH1_P = data.CH1_P
        self.current_CH1_N = data.CH1_N
        self.current_CH1_M = data.CH1_M
        self.current_CH2_P = data.CH2_P
        self.current_CH2_N = data.CH2_N
        self.current_CH2_M = data.CH2_M
        print(f"Updated data: {data}.")