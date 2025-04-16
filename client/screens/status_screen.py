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
        
    def update_bypass(self, value: int):
        if value == 1:
            self.bypass_status_value = "ON"
        else:
            self.bypass_status_value = "OFF"
        Logger.debug(f"Update bypass successfully, val: {value}, {self.bypass_status_value}")

    def update_engine_hour(self, engine_hour: str):
        self.engine_hour_value = engine_hour
        Logger.debug(f"Update engine hour successfully, val: {engine_hour}")

    def update_voltage(self, voltage: str):
        self.voltage_value = voltage
        Logger.debug(f"Update engine hour successfully, val: {voltage}")

