import random
import time

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy_garden.graph import Graph, LinePlot
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from websocket.client import WebSocketClient
from screens.set_threshold_popup import SetThresholdPopup
from screens.loading_screen import LoadingScreen
from screens.error_popup import ErrorPopup
from screens.image_button import ImageButton
from kivy.uix.image import Image
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

@dataclass
class AnalyzerData:
    TimeStamp: float
    Input1_Raw: int
    Input2_Raw: int
    CH1_P: int
    CH1_N: int
    CH2_P: int
    CH2_N: int

class AnalyzerScreen(Screen):
    title = "Analyzer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_screen = LoadingScreen(timeout=5, on_timeout_callback=self.on_timeout)
        self.response_received = False
        self.threshold = 1500
        self.threshold_popup = SetThresholdPopup(
            on_confirm_callback=self.set_threshold
        )
        self.error_popup = ErrorPopup()
        self.bypass = 0 # indicate the button show or hide
        self._create_graph()

    def reset_data(self):
        self.start_time = time.time()
        self.event = Clock.schedule_interval(self.update_graph, 0.1)
        self.loading_screen.hide()
        self.threshold_popup.reset_state()
        self.error_popup.reset_state()
        
    def get_title(self):
        return self.title

    def stop(self):
        Clock.unschedule(self.update_graph)
        self.event.cancel()
        
    def _create_graph(self):
        self.graph = Graph(
            xlabel="Samples",
            ylabel="Amplitude",
            x_ticks_minor=5, 
            x_ticks_major=1, 
            y_ticks_minor=5,
            y_ticks_major=500,
            y_grid_label=True,
            x_grid_label=False,
            xmin=0,
            xmax=10,  
            ymin=0,
            ymax=3000, 
            padding=1,
            label_options={"color": [1, 1, 1, 1], "bold": True}
        )

        self.ch1_p_plot = LinePlot(color=[0, 1, 0, 1])
        self.ch1_p_plot.points = []
        self.ch1_p_data = []

        self.ch1_n_plot = LinePlot(color=[1, 0.5, 0, 1])
        self.ch1_n_plot.points = []
        self.ch1_n_data = []

        self.ch2_p_plot = LinePlot(color=[0, 0.5, 1, 1])
        self.ch2_p_plot.points = []
        self.ch2_p_data = []

        self.ch2_n_plot = LinePlot(color=[1, 0, 1, 1])
        self.ch2_n_plot.points = []
        self.ch2_n_data = []

        self.threshold_plot = LinePlot(color=[1, 0, 0, 1], line_width=1)
        self.threshold_plot.points = []

        self.graph.add_plot(self.ch1_p_plot)
        self.graph.add_plot(self.ch1_n_plot)
        self.graph.add_plot(self.ch2_p_plot)
        self.graph.add_plot(self.ch2_n_plot)
        self.graph.add_plot(self.threshold_plot)

        layout = BoxLayout(orientation="vertical")
        layout.add_widget(self.graph)

        legend_items = [
            ("T", [1, 0, 0, 1]),
            ("C1-P", [0, 1, 0, 1]),
            ("C1-N", [1, 0.5, 0, 1]),
            ("C2-P", [0, 0.5, 1, 1]),
            ("C2-N", [1, 0, 1, 1]),
        ]

        self.bp_button = ImageButton(
            source="assets/threshold.png",
            size_hint=(None, None),
            size=(30, 30),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"center_y": 0.5}
        )
        self.bp_button.bind(on_release=self.open_threshold_popup)
        self.hide_button() #default hide this button

        legend_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.1,
            padding=[10, 5],
            spacing=5
        )
        legend_layout.add_widget(self.bp_button)

        for name, color in legend_items:
            label = Label(text=name, color=color)
            legend_layout.add_widget(label)

        
        layout.add_widget(legend_layout)
        self.add_widget(layout)

    def update_graph(self, dt):
        current_time = time.time()
        current_second = int(current_time - self.start_time) 

        time_range = 10
        self.ch1_p_data = [
            (timestamp,value) for timestamp, value in self.ch1_p_data if current_time - timestamp <= time_range
        ]

        self.ch1_n_data = [
            (timestamp,value) for timestamp, value in self.ch1_n_data if current_time - timestamp <= time_range
        ]

        self.ch2_p_data = [
            (timestamp,value) for timestamp, value in self.ch2_p_data if current_time - timestamp <= time_range
        ]

        self.ch2_n_data = [
            (timestamp,value) for timestamp, value in self.ch2_n_data if current_time - timestamp <= time_range
        ]

        self.ch1_n_plot.points = [(timestamp - self.start_time, value) for timestamp, value in self.ch1_n_data]
        self.ch1_p_plot.points = [(timestamp - self.start_time, value) for timestamp, value in self.ch1_p_data]
        self.ch2_n_plot.points = [(timestamp - self.start_time, value) for timestamp, value in self.ch2_n_data]
        self.ch2_p_plot.points = [(timestamp - self.start_time, value) for timestamp, value in self.ch2_p_data]

        self.threshold_plot.points = [
            (current_second - 11, self.threshold),
            (current_second + 2, self.threshold),
        ]

        self.graph.xmin = max(0, current_second - 10)
        self.graph.xmax = max(current_second + 1, 1)

    def update_data(self, data: AnalyzerData):
        self.ch1_n_data.append((data.TimeStamp, data.CH1_N))
        self.ch1_p_data.append((data.TimeStamp, data.CH1_P))
        self.ch2_n_data.append((data.TimeStamp, data.CH2_N))
        self.ch2_p_data.append((data.TimeStamp, data.CH2_P))

    def update_threshold(self, threshold: int):
        self.threshold = threshold

    def update_set_threshold_status(self, success: bool):
        self.response_received = True
        if success:
            self.loading_screen.hide()
            print("Set threshold to controller successful!")
        else:
            self.loading_screen.hide() 
            self.show_error_popup("Set threshold failed! Please try again.")

    def open_threshold_popup(self, instance):
        self.threshold_popup.handle_open()

    def set_threshold(self, new_threshold):
        if not WebSocketClient.instance().is_connected(): 
            self.show_error_popup("Cannot reset without connectting with server")
            return
        
        self.threshold = new_threshold
        self.response_received = False
        msg = SetThresholdRequest.create_message(threshold=self.threshold)
        WebSocketClient.instance().send_json_sync(
            msg.to_json()
        )
        print(f"Threshold updated to {self.threshold}")
        self.loading_screen.show()

    def on_timeout(self):
        self.loading_screen.hide()
        if not self.response_received:  
           self.show_error_popup("Request timed out! Please try again.")
    
    def show_error_popup(self, message):
        self.error_popup.update_message(message)
        self.error_popup.handle_open()

    def handle_on_enter(self) -> bool:
        if not self.enable_bypass():
            print("analyzer screen is not handle enter when not enable bypass mode.")
            return
        
        if self.is_showing_threshold_popup():
            self.threshold_popup.handle_on_enter()
            return True
        elif self.is_showing_error_popup():
            self.error_popup.handle_on_enter()
            return True
        elif self.is_showing_loading_screen():
            print(f"analyzer screen ignore to handle handle_on_enter.")
            return True
        self.open_threshold_popup(self)
        print("analyzer screen handle_on_enter")
        return True

    def on_down_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_down_pressed()
            return True
        
        print("analyzer screen not handle on_down_pressed")
        return False

    def on_up_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_up_pressed()
            return True
        print("analyzer screen not handle on_up_pressed")
        return False

    def on_left_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_left_pressed()
            return True
        elif self.is_showing_error_popup() or self.is_showing_loading_screen():
            print("analyzer screen ingore on_left_pressed")
            return True
        print("analyzer screen not handle on_left_pressed")
        return False

    def on_right_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_right_pressed()
            return True
        elif self.is_showing_error_popup() or self.is_showing_loading_screen():
            print("analyzer screen ingore on_right_pressed")
            return True
        print("analyzer screen not handle on_right_pressed")
        return False

    def is_showing_threshold_popup(self) -> bool:
        return self.threshold_popup.is_showing()
    
    def is_showing_error_popup(self) -> bool:
        return self.error_popup.is_showing()
    
    def is_showing_loading_screen(self) -> bool:
        return self.loading_screen.is_showing()
    
    def is_showing_popup_or_loading_screen(self):
        if self.is_showing_threshold_popup() or self.is_showing_error_popup() or self.is_showing_loading_screen():
            return True
        return False

    def update_bypass(self, value: int):
        self.bypass = value
        if self.bypass == 1:
            self.show_button()
        else:
            self.hide_button()
        print(f"analyzer screen update bypass successfully, val: {self.bypass}")

    def hide_button(self):
        self.bp_button.opacity = 0

    def show_button(self):
        self.bp_button.opacity = 1

    def enable_bypass(self) -> bool:
        return self.bypass == 1