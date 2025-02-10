from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import asyncio
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bypass = 1
        
    def reset_data(self):
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

    def on_brightness_change(self, value: int):
        self.brightness = value
        print("Update brightness of LCD screen successully.")

    def on_copy_log_click(self):
        print("Copy log successfully.")

    def on_reset_factory_click(self):
        popup_layout = BoxLayout(orientation="vertical", padding=5, spacing=5)

        message_label = Label(
            text="Reset settings?",
            halign="center",
            valign="middle",
            size_hint=(1, 0.6), 
        )
        message_label.bind(size=message_label.setter("text_size"))  # Wrap text properly
        popup_layout.add_widget(message_label)

        button_layout = BoxLayout(orientation="horizontal", spacing=5, size_hint=(1, 0.4))

        cancel_button = Button(
            text="Cancel",
            size_hint=(0.5, 1),
            background_color=(0.5, 0.5, 0.5, 1),
        )
        confirm_button = Button(
            text="Reset",
            size_hint=(0.5, 1),
            background_color=(1, 0, 0, 1),
        )

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)
        popup_layout.add_widget(button_layout)

        popup = Popup(
            title="Reset Factory",
            content=popup_layout,
            size_hint=(None, None),
            size=(320, 200),
        )

        cancel_button.bind(on_release=popup.dismiss)
        confirm_button.bind(on_release=lambda _: self.reset_factory(popup))

        popup.open()


    
    def reset_factory(self, popup):
        msg = SetDefaultCalibrationRequest.create_message()
        WebSocketClient.instance().send_json_sync(
            msg.to_json()
        )
        print("Settings have been reset to default.")

        popup.dismiss() 