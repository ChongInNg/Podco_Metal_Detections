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
        self._create_graph()

    def reset_data(self):
        self.start_time = time.time()
        self.event = Clock.schedule_interval(self.update_graph, 0.1)
        self.loading_screen.hide()
        
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

        self.threshold_plot = LinePlot(color=[1, 0, 0, 1], line_width=2)
        self.threshold_plot.points = []

        self.threshold_plot = LinePlot(color=[1, 0, 0, 1], line_width=2)
        self.threshold_plot.points = []

        self.graph.add_plot(self.ch1_p_plot)
        self.graph.add_plot(self.ch1_n_plot)
        self.graph.add_plot(self.ch2_p_plot)
        self.graph.add_plot(self.ch2_n_plot)
        self.graph.add_plot(self.threshold_plot)

        layout = BoxLayout(orientation="vertical")
        layout.add_widget(self.graph)

        legend_layout = BoxLayout(size_hint_y=0.1)

        legend_items = [
            ("T", [1, 0, 0, 1]),
            ("CH1 P", [0, 1, 0, 1]),
            ("CH1 N", [1, 0.5, 0, 1]),
            ("CH2 P", [0, 0.5, 1, 1]),
            ("CH2 N", [1, 0, 1, 1]),
        ]

        self.bp_button = Button(text="BP", size_hint_x=0.2, 
            on_press=self.open_threshold_popup)
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
        popup = SetThresholdPopup(
            on_confirm_callback=self.set_threshold
        )
        popup.open()

    def set_threshold(self, new_threshold):
        self.threshold = new_threshold

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
        error_popup = ErrorPopup(message=message)
        error_popup.open()