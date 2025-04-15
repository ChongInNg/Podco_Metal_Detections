from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from config.config import ConfigManager
import threading
import sys
import os
import time
from log.logger import Logger

Builder.load_file("kv/status_screen.kv")

class StatusScreen(Screen):
    title = StringProperty('Status')
    voltage_value = StringProperty("0")
    bypass_status_value = StringProperty("OFF")
    engine_hour_value = StringProperty("0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_kv_post(self, base_widget):
       self.reset_data()

    def reset_data(self):
        pass

    def get_title(self):
        return self.title
    
    def on_back_btn_click(self):
        self.reset_data()
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_screen_name("option")
        
    def update_bypass(self, value: int):
        if value == 1:
            self.bypass_status_value = "ON"
        else:
            self.bypass_status_value = "OFF"
        Logger.debug(f"Update bypass successfully, val: {value}, {self.bypass_status_value}")

    def handle_on_enter(self):
        pass

    def clear_focus(self):
        pass

    def handle_on_enter(self):
        pass
