from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

Builder.load_file("kv/detection_screen.kv")


@dataclass
class DetectionViewData:
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

    def reset_data(self):
        self.current_index = 0
        self.update_current_values()

    def get_title(self):
        return self.title
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detections = []

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

    def add_detection(self, detection_data: DetectionViewData):
        if len(self.detections) >= 10:
            del self.detections[0]
            print(f"Popup the first detection")
        
        self.detections.append(detection_data)
        self.current_index = 0
        self.update_current_values()

    def init_detections(self, detections: DetectionLogs):
        self.detections.clear()
        for detection in detections.logs:
            self.detections.append(DetectionViewData(
                T_Value=str(detection.t_value),
                D_Value=str(detection.d_value),
                CH1_P=str(detection.ch1_area_p),
                CH1_N=str(detection.ch1_area_n),
                CH2_P=str(detection.ch2_area_p),
                CH2_N=str(detection.ch2_area_n),
            ))