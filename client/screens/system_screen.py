from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from log.logger import Logger
from websocket.client import WebSocketClient
from screens.loading_screen import LoadingScreen
from screens.common_popup import CommonPopup
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import GetFirmwareVersionRequest, GetHardwareVersionRequest

Builder.load_file("kv/system_screen.kv")

DEFAULT_VERSION:str = "N/A"
class SystemScreen(Screen):
    title = StringProperty('System')
    firmware_version = StringProperty(DEFAULT_VERSION)
    hardware_version = StringProperty(DEFAULT_VERSION)
    current_button = StringProperty('upgrade_btn')
    
    button_ids = ['upgrade_btn', 'rollback_btn', 'back_btn']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_upgrading = False
        
        self.loading_screen = LoadingScreen(
            timeout=3,
            on_timeout_callback=self.on_version_request_timeout
        )
        
        self.common_popup = CommonPopup()
        
        self.firmware_response_received = False
        self.hardware_response_received = False
    
    def on_kv_post(self, base_widget):
        self.reset_data()

    def reset_data(self):
        self.current_button = 'upgrade_btn'
        self.set_focus_button(self.current_button)
        self.request_versions()

    def request_versions(self):
        if not WebSocketClient.instance().is_connected():
            Logger.warning("WebSocket not connected, cannot request versions")
            self.firmware_version = DEFAULT_VERSION
            self.hardware_version = DEFAULT_VERSION
            return
    
        self.firmware_response_received = False
        self.hardware_response_received = False
   
        self.loading_screen.update_message("Loading versions...")
        self.loading_screen.show(enable_timeout=True)

        firmware_msg = GetFirmwareVersionRequest.create_message()
        WebSocketClient.instance().send_json_sync(firmware_msg.to_json())
        Logger.debug("Sent GetFirmwareVersionRequest to server")

        hardware_msg = GetHardwareVersionRequest.create_message()
        WebSocketClient.instance().send_json_sync(hardware_msg.to_json())
        Logger.debug("Sent GetHardwareVersionRequest to server")

    def update_firmware_version_ack(self):
        Logger.debug("Received get firmware version ack")

    def update_hardware_version_ack(self):
        Logger.debug("Received get hardware version ack")

    def update_firmware_version_response(self, major: int, minor:int, bugfix: int):
        self.firmware_response_received = True
        self.firmware_version = f"{major}.{minor}.{bugfix}"
        Logger.debug(f"Firmware version updated: { self.firmware_version}")
        
        self.check_all_responses_received()

    def update_hardware_version_response(self, major: int, minor:int, bugfix: int):
        self.hardware_response_received = True
        self.hardware_version = f"{major}.{minor}.{bugfix}"
        Logger.debug(f"Hardware version updated: {self.hardware_version}")

        self.check_all_responses_received()

    def check_all_responses_received(self):
        if self.firmware_response_received and self.hardware_response_received:
            Logger.debug("Both version responses received, hiding loading screen")
            self.loading_screen.hide()

    def on_version_request_timeout(self):
        Logger.warning("Version request timed out")

        if not self.firmware_response_received:
            self.firmware_version = DEFAULT_VERSION
        if not self.hardware_response_received:
            self.hardware_version = DEFAULT_VERSION
        
        self.show_error_popup("Request timed out! Please try again.")

    def show_error_popup(self, message):
        self.common_popup.update_title("Error")
        self.common_popup.update_message(message)
        self.common_popup.handle_open()

    def get_title(self):
        return self.title

    def on_up_pressed(self):
        if self.loading_screen.is_showing():
            Logger.debug("loading screen is showing. ignore up pressed.")
            return
        if self.common_popup.is_showing():
            Logger.debug("popup is showing, ignore up pressed")
            return
        
        current_index = self.button_ids.index(self.current_button)
        new_index = (current_index - 1) % len(self.button_ids)
        self.current_button = self.button_ids[new_index]
        self.set_focus_button(self.current_button)
    
    def on_down_pressed(self):
        if self.loading_screen.is_showing():
            Logger.debug("loading screen is showing. ignore down pressed.")
            return
        if self.common_popup.is_showing():
            Logger.debug("popup is showing, ignore down pressed")
            return
        
        current_index = self.button_ids.index(self.current_button)
        new_index = (current_index + 1) % len(self.button_ids)
        self.current_button = self.button_ids[new_index]
        self.set_focus_button(self.current_button)

    def clear_focus(self):
        for button_id in self.button_ids:
            if button_id in self.ids:
                self.ids[button_id].state = "normal"

    def set_focus_button(self, focused_button_id):
        self.clear_focus()
        if focused_button_id in self.ids:
            self.ids[focused_button_id].state = "down"

    def handle_on_enter(self):
        if self.loading_screen.is_showing():
            Logger.debug("loading scree is showing, ignore enter pressed")
            return
        
        if self.common_popup.is_showing():
            Logger.debug("pop up is showing, dismiss it when enter pressed")
            self.dismiss_popups()
            return
        
        if self.current_button == 'upgrade_btn':
            self.on_upgrade_btn_click()
        elif self.current_button == 'rollback_btn':
            self.on_rollback_btn_click()
        elif self.current_button == 'back_btn':
            self.on_back_btn_click()
        
    def on_upgrade_btn_click(self):
        if self.is_upgrading:
            Logger.debug("Upgrade already in progress")
            return
        
        Logger.debug("Starting upgrade process...")
        self.is_upgrading = True

    def on_rollback_btn_click(self):
        Logger.debug("Rollback button clicked")
        pass

    def on_back_btn_click(self):
        Logger.debug("Back button clicked")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_option_screen()

    def show_popups(self):
        if self.common_popup.is_showing():
            self.common_popup.opacity = 1

    def dismiss_popups(self):
        if self.common_popup.is_showing():
            self.common_popup.opacity = 1
            self.common_popup.handle_dismiss(self)
