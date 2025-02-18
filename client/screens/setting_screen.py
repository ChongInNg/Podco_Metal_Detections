from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock
from screens.loading_screen import LoadingScreen
from screens.error_popup import ErrorPopup
from screens.confirmation_popup import ConfirmationPopup

import sys
import os

from websocket.client import WebSocketClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

Builder.load_file("kv/setting_screen.kv")

class SettingScreen(Screen):
    title = StringProperty('Setting')
    brightness = NumericProperty(50)
    bypass_status = NumericProperty(0)
    bypass_status_value = StringProperty("OFF")
    current_button = StringProperty('')
    button_ids = ["reset_factory_btn", "copy_log_btn", "back_btn"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bypass = 1
        self.loading_screen = LoadingScreen(timeout=5, on_timeout_callback=self.on_timeout)
        self.copy_loading_screen = LoadingScreen(message="Copying", timeout=5, on_timeout_callback=self.on_copy_timeout)
        self.response_received = False

    def reset_data(self):
        self.current_button = ""
        self.clear_focus()
        pass

    def get_title(self):
        return self.title
    
    def on_back_btn_click(self):
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_screen_name("option")

    def update_bypass(self, value: int):
        self.bypass = value
        if self.bypass == 1:
            self.bypass_status_value = "ON"
        else:
            self.bypass_status_value = "OFF"
        print(f"Update bypass successfully, val: {self.bypass}, {self.bypass_status_value}")

    def update_reset_factory_status(self, success: bool):
        self.response_received = True
        if success:
            self.loading_screen.hide()
            print("Reset factory config to controller successful!")
        else:
            self.loading_screen.hide() 
            self.show_error_popup("Reset failed! Please try again.")

    def on_brightness_change(self, value: int):
        self.brightness = value
        print("Update brightness of LCD screen successully.")

    def on_copy_log_click(self):
        self.copy_loading_screen.show()
        print("Copy log successfully.")

    def on_reset_factory_click(self):
        reset_popup = ConfirmationPopup(
            title="Reset Factory",
            message="Reset settings to defaults?",
            on_confirm_callback=self.reset_factory
        )
        reset_popup.open()

    def reset_factory(self):
        self.response_received = False
        self.copy_loading_screen.show()
        msg = SetDefaultCalibrationRequest.create_message()
        WebSocketClient.instance().send_json_sync(
            msg.to_json()
        )
    
        print("Send set_default_calibration message to server successfully.")
        
    def show_error_popup(self, message):
        error_popup = ErrorPopup(message=message)
        error_popup.open()
          
    def on_timeout(self):
        self.loading_screen.hide()
        if not self.response_received:  
           self.show_error_popup("Request timed out! Please try again.")

    def on_copy_timeout(self):
        self.copy_loading_screen.hide()
        self.show_error_popup("Copy timed out! Please try again.")
           
    def clear_focus(self):
        for button_id in self.button_ids:
            button = self.ids[button_id]
            button.state = "normal"

    def set_focus_button(self, focused_button_id):
        self.clear_focus()

        focused_button = self.ids[focused_button_id]
        focused_button.state = "down"


    def handle_on_enter(self):
        if self.current_button == "reset_factory_btn":
            self.on_reset_factory_click()
        elif self.current_button == "copy_log_btn":
            self.on_copy_log_click()
        elif self.current_button == "back_btn":
            self.on_back_btn_click()
        print("setting screen handle_on_enter")

    def on_down_pressed(self):
        if self.current_button == "":
            self.current_button = self.button_ids[len(self.button_ids) - 1]
            self.set_focus_button(self.current_button)
        else:
            current_index = self.button_ids.index(self.current_button)
            new_index = (current_index + 1) % len(self.button_ids)
            self.current_button = self.button_ids[new_index]
            self.set_focus_button(self.current_button)
        print("setting screen on_down_pressed")

    def on_up_pressed(self):
        if self.current_button == "":
            self.current_button = self.button_ids[0]
            self.set_focus_button(self.current_button)
        else:
            current_index = self.button_ids.index(self.current_button)
            new_index = (current_index - 1) % len(self.button_ids)
            self.current_button = self.button_ids[new_index]
            self.set_focus_button(self.current_button)

        print("setting screen on_up_pressed")

    def on_left_pressed(self):
        print("setting screen on_left_pressed")

    def on_right_pressed(self):
        print("setting screen on_right_pressed")