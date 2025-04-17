import random
import time

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy_garden.graph import Graph, LinePlot
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from websocket.client import WebSocketClient
from screens.set_threshold_popup import SetThresholdPopup
from screens.loading_screen import LoadingScreen
from screens.common_popup import CommonPopup
from screens.image_button import ImageButton
from dataclasses import dataclass
from log.logger import Logger
from kivy.uix.image import Image

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
        self.threshold = 1000
        self.pending_threshold = 0
        self.threshold_popup = SetThresholdPopup(
            on_confirm_callback=self.set_threshold_by_popup
        )
        
        self.error_popup = CommonPopup()
        self.bypass = 0 # indicate the button show or hide
        self.is_pause = False
        self._create_graph()

    def reset_data(self):
        # self.hide_over_threshold_indicator()
        # self.hide_pause_image()

        self.start_update_graph()
        self.loading_screen.hide()
        self.threshold_popup.reset_state()
        self.error_popup.reset_state()
        
    def get_title(self):
        return self.title

    def start_update_graph(self):
        self.event = Clock.schedule_interval(self.update_graph, 0.1)

    def stop_update_graph(self):
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
            size=(48, 48),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"center_y": 0.5}
        )
        self.bp_button.bind(on_release=self.open_threshold_popup)
        self.hide_bypass_button() #default hide this button

        self.pause_img = Image(
            source="assets/pause_icon.png",
            size_hint=(None, None),
            size=(40, 28),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"center_y": 0.5}
        )
        self.hide_pause_image()

        legend_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.1,
            padding=[5,1,5,5],
            spacing=5
        )
        legend_layout.add_widget(self.bp_button)
        legend_layout.add_widget(self.pause_img)
        for name, color in legend_items:
            label = Label(text=name, color=color)
            legend_layout.add_widget(label)

        
        layout.add_widget(legend_layout)
        self.add_widget(layout)

    def update_graph(self, dt):
        current_time = time.time()
        current_second = int(current_time) 

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

        if self.is_over_threshold(self.ch1_n_data, self.ch1_p_data, self.ch2_n_data, self.ch2_p_data):
            self.show_over_threshold_indicator()
        else:
            self.hide_over_threshold_indicator()
        
        self.ch1_n_plot.points = self.ch1_n_data
        self.ch1_p_plot.points = self.ch1_p_data
        self.ch2_n_plot.points = self.ch2_n_data
        self.ch2_p_plot.points = self.ch2_p_data

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
        self.threshold_popup.update_threshold(threshold)

    def update_set_threshold_status(self, success: bool):
        self.response_received = True
        if success:
            self.loading_screen.hide()
            self.threshold = self.pending_threshold
            self.threshold_popup.update_threshold(self.threshold)
            self.pending_threshold = 0
            Logger.debug("Set threshold to controller successful!")
        else:
            self.threshold_popup.update_threshold(self.threshold)
            self.pending_threshold = 0
            self.loading_screen.hide() 
            self.show_error_popup("Set threshold failed! Please try again.")

    def open_threshold_popup(self, instance):
        self.threshold_popup.handle_open()
    
    def handle_pause(self, instance):
        self.is_pause = not self.is_pause
        if self.is_pause:
            self.stop_update_graph()
            self.show_pause_image()
        else:
            self.start_update_graph()
            self.hide_pause_image()

    def set_threshold_by_popup(self, new_threshold):
        if not WebSocketClient.instance().is_connected(): 
            self.show_error_popup("Cannot reset without connectting with server")
            return
        
        self.pending_threshold = new_threshold
        self.response_received = False
        msg = SetThresholdRequest.create_message(threshold=self.pending_threshold)
        WebSocketClient.instance().send_json_sync(
            msg.to_json()
        )
        Logger.debug(f"Threshold will be updated to {self.pending_threshold}")
        self.loading_screen.show()

    def on_timeout(self):
        self.loading_screen.hide()
        self.threshold_popup.update_threshold(self.threshold)
        self.pending_threshold = 0
        self.threshold_popup.reset_state()
        if not self.response_received:  
           self.show_error_popup("Request timed out! Please try again.")
    
    def show_error_popup(self, message):
        self.error_popup.update_message(message)
        self.error_popup.handle_open()

    def handle_on_up_down(self) -> bool:
        if not self.enable_bypass():
            Logger.debug("analyzer screen is not handle up_down when not enable bypass mode.")
            return False 

        if self.is_showing_threshold_popup():
            Logger.debug("analyzer screen is not handle up_down when is showing threshold popup.")
            return False 
        elif self.is_showing_error_popup():
            Logger.debug("analyzer screen is not handle up_down when is showing error popup.")
            return False
        elif self.is_showing_loading_screen():
            Logger.debug("analyzer screen is not handle up_down when is showing loading_scree.")
            return False
        
        self.open_threshold_popup(self)
        return True
    
    def handle_on_enter(self) -> bool:
        if not self.enable_bypass():
            Logger.debug("analyzer screen is not handle enter when not enable bypass mode.")
            return False
        
        if self.is_showing_threshold_popup():
            self.threshold_popup.handle_on_enter()
            return True
        elif self.is_showing_error_popup():
            self.error_popup.handle_on_enter()
            return True
        elif self.is_showing_loading_screen():
            Logger.debug(f"analyzer screen ignore to handle handle_on_enter.")
            return True
        # self.open_threshold_popup(self)
        self.handle_pause(self)
        Logger.debug("analyzer screen handle_on_enter")
        return True

    def on_down_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_down_pressed()
            return True
        
        Logger.debug("analyzer screen not handle on_down_pressed")
        return False

    def on_up_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_up_pressed()
            return True
        Logger.debug("analyzer screen not handle on_up_pressed")
        return False

    def on_left_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_left_pressed()
            return True
        elif self.is_showing_error_popup() or self.is_showing_loading_screen():
            Logger.debug("analyzer screen ingore on_left_pressed")
            return True
        Logger.debug("analyzer screen not handle on_left_pressed")
        return False

    def on_right_pressed(self) -> bool:
        if self.is_showing_threshold_popup():
            self.threshold_popup.on_right_pressed()
            return True
        elif self.is_showing_error_popup() or self.is_showing_loading_screen():
            Logger.debug("analyzer screen ingore on_right_pressed")
            return True
        Logger.debug("analyzer screen not handle on_right_pressed")
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
            self.show_bypass_button()
        else:
            self.hide_bypass_button()
            
            self.hide_pause_image()
            self.is_pause = False
        
        Logger.debug(f"analyzer screen update bypass successfully, val: {self.bypass}")

    def hide_bypass_button(self):
        # self.bp_button.opacity = 0
        self.bp_button.size = (0, 0)
        self.bp_button.size_hint = (None, None)

    def show_bypass_button(self):
        # self.bp_button.opacity = 1
        self.bp_button.size = (48, 48)
        self.bp_button.size_hint = (None, None)

    def hide_pause_image(self):
        self.pause_img.size = (0, 0)
        self.pause_img.size_hint = (None, None)

    def show_pause_image(self):
        self.pause_img.size = (40, 28)
        self.pause_img.size_hint = (None, None)

    def enable_bypass(self) -> bool:
        return self.bypass == 1
    
    def hide_popups(self):
        if self.error_popup.is_showing():
            self.error_popup.opacity = 0
            Logger.debug("analyzer screen hide_popups")

    def show_popups(self):
        if self.error_popup.is_showing():
            self.error_popup.opacity = 1
            Logger.debug("analyzer screen show_popups")

    def dismiss_popups(self):
        if self.is_showing_error_popup():
            if self.error_popup.opacity != 1: 
                #only popup hiding when user idle to logo screen,
                # then the admin user login
                self.error_popup.opacity = 1 
            self.error_popup.handle_dismiss()

    def show_over_threshold_indicator(self):
        self.bp_button.source = "assets/threshold_red.png"

    def hide_over_threshold_indicator(self):
        self.bp_button.source = "assets/threshold.png"

    def is_over_threshold(self, ch1_n_data: list, ch1_p_data: list, ch2_n_data: list, ch2_p_data: list) -> bool:
        for _, value in ch1_n_data:
            if value >= self.threshold:
                return True
        for _, value in ch1_p_data:
            if value >= self.threshold:
                return True
        
        for _, value in ch2_n_data:
            if value >= self.threshold:
                return True
        for _, value in ch2_p_data:
            if value >= self.threshold:
                return True
        return False
