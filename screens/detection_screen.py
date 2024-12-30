from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from dataclasses import dataclass

Builder.load_file("kv/detection_screen.kv")


@dataclass
class DetectionData:
    T_Value: str
    D_Value: str
    CH1_P: str
    CH1_N: str
    CH2_P: str
    CH2_N: str


class DetectionScreen(Screen):
    title = StringProperty('Detection')

    current_page = StringProperty("No. 1")
    current_T = StringProperty("0")
    current_D = StringProperty("0")
    current_CH1_P = StringProperty("0")
    current_CH1_N = StringProperty("0")
    current_CH2_P = StringProperty("0")
    current_CH2_N = StringProperty("0")


    current_index = NumericProperty(0)
    detections = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detections = [
            DetectionData(
                T_Value=str(i * 10),
                D_Value=str(i * 20),
                CH1_P=str(i * 30),
                CH1_N=str(i * 40),
                CH2_P=str(i * 50),
                CH2_N=str(i * 60),
            )
            for i in range(1, 11)
        ]

    def on_kv_post(self, base_widget):
        self.update_current_values()

    def update_current_values(self):
        if 0 <= self.current_index < len(self.detections):
            detection = self.detections[self.current_index]
            self.current_page = f"No. {self.current_index + 1}"
            self.current_T = detection.T_Value
            self.current_D = detection.D_Value
            self.current_CH1_P = detection.CH1_P
            self.current_CH1_N = detection.CH1_N
            self.current_CH2_P = detection.CH2_P
            self.current_CH2_N = detection.CH2_N

        self.update_btn_visiable()

    def on_up_pressed(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_current_values()

    def on_down_pressed(self):
        if self.current_index < len(self.detections) - 1:
            self.current_index += 1
            self.update_current_values()
    
    def update_btn_visiable(self):
        up_btn = self.ids.up_btn
        down_btn = self.ids.down_btn

        if self.current_index == 0:
            up_btn.opacity = 0 
            up_btn.disabled = True
        else:
            up_btn.opacity = 1
            up_btn.disabled = False

        if self.current_index == len(self.detections) - 1:
            down_btn.opacity = 0
            down_btn.disabled = True
        else:
            down_btn.opacity = 1
            down_btn.disabled = False
