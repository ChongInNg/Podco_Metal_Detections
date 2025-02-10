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

    def reset_data(self):
        self.start_time = time.time()
        self.event = Clock.schedule_interval(self.update_graph, 0.1)
        
    def get_title(self):
        return self.title

    def stop(self):
        Clock.unschedule(self.update_graph)
        self.event.cancel()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.threshold = 1500
        self._create_graph()
        
    def _create_graph(self):
        self.graph = Graph(
            xlabel="Time (s)",
            ylabel="Amplitude",
            x_ticks_minor=5, 
            x_ticks_major=1, 
            y_ticks_minor=5,
            y_ticks_major=500,
            y_grid_label=True,
            x_grid_label=True,
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

        # contol the graph view size in around 10 seconds
        self.graph.xmin = max(0, current_second - 10)
        self.graph.xmax = max(current_second + 1, 1)

    def update_data(self, data: AnalyzerData):
        self.ch1_n_data.append((data.TimeStamp, data.CH1_N))
        self.ch1_p_data.append((data.TimeStamp, data.CH1_P))
        self.ch2_n_data.append((data.TimeStamp, data.CH2_N))
        self.ch2_p_data.append((data.TimeStamp, data.CH2_P))

    def update_threshold(self, threshold: int):
        self.threshold = threshold

    def open_threshold_popup(self, instance):
        popup_layout = BoxLayout(orientation="vertical", spacing=5, padding=5)

        label = Label(text=f"Threshold: {self.threshold}", font_size=14, size_hint_y=0.2)

        slider = Slider(min=500, max=2500, value=self.threshold, size_hint_y=0.4)
        slider.bind(value=lambda instance, val: setattr(label, 'text', f"Threshold: {int(val)}"))

        button_layout = BoxLayout(size_hint_y=0.5, spacing=5)

        confirm_button = Button(text="Confirm", size_hint=(0.5, 0.8), font_size=14)
        confirm_button.bind(on_press=lambda x: self.set_threshold(int(slider.value), popup))

        cancel_button = Button(text="Cancel", size_hint=(0.5, 0.8), font_size=14)
        cancel_button.bind(on_press=lambda x: popup.dismiss())

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)

        popup_layout.add_widget(label)
        popup_layout.add_widget(slider)
        popup_layout.add_widget(button_layout)

        popup = Popup(
            title="Set Threshold",
            content=popup_layout,
            size_hint=(None, None),
            size=(320, 200),
        )

        popup.open()

    def set_threshold(self, new_threshold, popup):
        self.threshold = new_threshold

        msg = SetThresholdRequest.create_message(threshold=self.threshold)
        WebSocketClient.instance().send_json_sync(
            msg.to_json()
        )
        print(f"Threshold updated to {self.threshold}")
        popup.dismiss()