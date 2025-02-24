from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.lang import Builder
from kivy.clock import Clock
from screens.loading_screen import LoadingScreen
from screens.common_popup import CommonPopup
from screens.confirmation_popup import ConfirmationPopup
from config.config import ConfigManager
from controller.device_detector import DeviceDetector
from controller.file_operation import FileOperation
import threading
import sys
import os
import time

from websocket.client import WebSocketClient
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

Builder.load_file("kv/setting_screen.kv")

class SettingScreen(Screen):
    title = StringProperty('Settings')
    brightness = NumericProperty(0)
    bypass_status = NumericProperty(0)
    bypass_status_value = StringProperty("OFF")
    component_ids = component_ids = [
        ("brightness_slider", "slider"),
        ("reset_factory_btn", "button"),
        ("copy_log_btn", "button"),
        ("back_btn", "button"),
    ]

    HIGHLIGHT_slider_color = [0.196, 0.643, 0.808,1]
    DEFAULT_slider_color = [0.15, 0.15, 0.2, 1]
    
    slider_color = ListProperty(DEFAULT_slider_color)
    # reset_button_color = ListProperty([1, 0, 0, 1]) 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brightness = ConfigManager.instance().brightness
        self.brightness_step = ConfigManager.instance().brightness_step
        self.bypass = 1
        self.loading_screen = LoadingScreen(timeout=5, on_timeout_callback=self.on_timeout)
     
        self.response_received = False
        self.current_component_id = ""
        self.bg_pwm = None
        self.reset_popup = ConfirmationPopup(
            title="Reset Factory",
            message="Reset settings to defaults?",
            on_confirm_callback=self.reset_factory
        )

        self.common_popup = CommonPopup()
    
    def on_kv_post(self, base_widget):
       self.reset_data()
       self.apply_brightness_to_lcd(self.brightness)

    def reset_data(self):
        self.reset_popup.reset_state()
        self.common_popup.reset_state()

        self.clear_focus()
        self.current_component_id = "brightness_slider"
        self.highlight_slider() # default make slider high light

    def get_title(self):
        return self.title
    
    def on_back_btn_click(self):
        if self.brightness != ConfigManager.instance().brightness:
            if not ConfigManager.instance().save_brightness(self.brightness):
                self.show_error_popup("Save brigntness data error.")
                return

        self.reset_data()
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
        self.loading_screen_for = ""
        if success:
            self.loading_screen.hide()
            print("Reset factory config to controller successful!")
        else:
            self.loading_screen.hide()
            self.show_error_popup("Reset failed! Please try again.")

    def on_brightness_change(self, value: float):
        self.brightness = int(round(value))
        self.apply_brightness_to_lcd(self.brightness)
        print("Update brightness of LCD screen successully.")

    def on_copy_log_click(self):
        device_detector = DeviceDetector(mount_point=ConfigManager.instance().mount_point)
        if ConfigManager.instance().run_on_rpi():
            exist = device_detector.detect()
            if not exist:
                self.show_error_popup("Cannot detect usb device, cannot copy now.")
                return
        
        self.loading_screen.update_message("Copying")
        self.loading_screen_for = "copying"
        self.loading_screen.show()

        copy_thread = threading.Thread(target=self._copy_files, args=(device_detector,), daemon=True)
        copy_thread.start()
        print("Copy log successfully.")

    def on_reset_factory_click(self):
        self.reset_popup.handle_open()

    def reset_factory(self):
        if not WebSocketClient.instance().is_connected(): 
            self.show_error_popup("Cannot reset without connectting with server")
            return
        self.response_received = False
        self.loading_screen.update_message("Waitting for response")
        self.loading_screen.show()
        self.loading_screen_for = "reset"
        msg = SetDefaultCalibrationRequest.create_message()
        WebSocketClient.instance().send_json_sync(
            msg.to_json()
        )
    
        print("Send set_default_calibration message to server successfully.")
        
    def show_error_popup(self, message):
        self.common_popup.update_title("Error")
        self.common_popup.update_message(message)
        self.common_popup.handle_open()

    def show_confirmation_popup(self, message):
        self.common_popup.update_title("Confirmation")
        self.common_popup.update_message(message)
        self.common_popup.handle_open()
    
    def on_timeout(self):
        self.loading_screen.hide()
        if self.loading_screen_for == "reset":
            if not self.response_received:  
                self.show_error_popup("Request timed out! Please try again.")
        else:
            self.show_error_popup("Copy timed out! Please try again.")
        
        self.loading_screen_for = ""

    def clear_focus(self):
        for component_id, component_type  in self.component_ids:
            component = self.ids[component_id]
            if component_type == "button":
                component.state = "normal"
            elif component_type == "slider":
                self.reset_slider_color()

    def set_focus_component(self, index: int):
        if index < 0 or index >= len(self.component_ids):
            print("Index is out of range, set_focus_component failed.")
            return

        self.clear_focus()
        component_id, component_type = self.component_ids[index]
        focused_component = self.ids[component_id]
        
        if component_type == "button":
            focused_component.state = "down"
        elif component_type == "slider":
            self.highlight_slider() 

        self.current_component_id = component_id

    def handle_on_enter(self):
        if self.current_component_id == "reset_factory_btn":
            if self.is_showing_reset_popup():
                self.reset_popup.handle_on_enter()
            elif self.is_showing_common_popup():
                self.common_popup.handle_on_enter()
            elif self.is_showing_loading_screen():
                print("Setting Screen is showing loading screen, no need to handle enter")
            else:
                self.on_reset_factory_click()

        elif self.current_component_id == "copy_log_btn":
            if self.is_showing_loading_screen():
                print("Setting Screen is copy log showing loading screen, no need to handle enter")
            elif self.is_showing_common_popup():
                self.common_popup.handle_on_enter()
            else:
                self.on_copy_log_click()
        elif self.current_component_id == "back_btn":
            self.on_back_btn_click()
        print("setting screen handle_on_enter")

    def on_down_pressed(self):
        if self.is_showing_popup_or_loading_screen():
            print("ingore on_down_pressed when setting screen is showing")
            return
         
        if self.current_component_id == "":
            new_index = len(self.component_ids) - 1
        else:
            current_index = self.get_current_index()
            new_index = (current_index + 1) % len(self.component_ids)
        
        self.set_focus_component(new_index) 
        print("setting screen on_down_pressed")

    def on_up_pressed(self):
        if self.is_showing_popup_or_loading_screen():
            print("ingore on_up_pressed when setting screen is showing")
            return
        
        if self.current_component_id == "":
            new_index = 0
        else:
            current_index = self.get_current_index()
            new_index = (current_index - 1) % len(self.component_ids)

        self.set_focus_component(new_index)
        print("setting screen on_up_pressed")

    def get_current_index(self) -> int:
        for i in range(len(self.component_ids)):
            if self.component_ids[i][0] == self.current_component_id:
                return i
        return -1

    def on_left_pressed(self):
        if self.is_showing_reset_popup():
            self.reset_popup.on_left_pressed()
        elif self.current_component_id == "brightness_slider":
            if self.brightness - self.brightness_step >= 10:
                self.brightness = self.brightness - self.brightness_step

        print("setting screen on_left_pressed")

    def on_right_pressed(self):
        if self.is_showing_reset_popup():
            self.reset_popup.on_right_pressed()
        elif self.current_component_id == "brightness_slider":
            if self.brightness + self.brightness_step <= 100:
                self.brightness = self.brightness + self.brightness_step
        print("setting screen on_right_pressed")
    
    def highlight_slider(self):
        self.slider_color = SettingScreen.HIGHLIGHT_slider_color
        print("highlight_slider.........")

    def reset_slider_color(self):
        self.slider_color = SettingScreen.DEFAULT_slider_color
        print("reset_slider_color.........")

    def is_showing_reset_popup(self) -> bool:
        return self.reset_popup.is_showing()
    
    def is_showing_common_popup(self) -> bool:
        return self.common_popup.is_showing()
    
    def is_showing_loading_screen(self) -> bool:
        return self.loading_screen.is_showing()
    
    def is_showing_popup_or_loading_screen(self):
        if self.is_showing_reset_popup() or self.is_showing_common_popup() or self.is_showing_loading_screen():
            return True
        return False
    
    def apply_brightness_to_lcd(self, brightness: int):
        if ConfigManager.instance().run_on_rpi():
            self._get_bg_pwm_instance().ChangeDutyCycle(brightness)
            print(f"set brigness {brightness} success.")
        else:
            print("Not run on rpi, cannot update brightness")

    def _get_bg_pwm_instance(self):
        if self.bg_pwm is None:
            import RPi.GPIO as GPIO
            bg_pin = 18
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(bg_pin, GPIO.OUT)
            self.bg_pwm = GPIO.PWM(bg_pin,1000)
            self.bg_pwm.start(0)
            
        return self.bg_pwm
    
    def _copy_files(self, device_detector: DeviceDetector):
        if not ConfigManager.instance().run_on_rpi():
            print("Not run on rasberry pi, cannot to copy files.")
            return

        src_folders = ConfigManager.instance().src_folders
        mount_point = device_detector.mount_point
        need_copy_files_suffix = ConfigManager.instance().need_copy_files_suffix
        file_operation = FileOperation(
            src_folders=src_folders, 
            mount_point=mount_point,
            need_copy_files_suffix=need_copy_files_suffix
        )
        total_copy = file_operation.copy_from_folders()
        # total_copy = 4
        print(f"Total copy {total_copy}")

        # device_detector.eject()
        # time.sleep(2)
        Clock.schedule_once(lambda dt: self._finish_copy(total_copy))

    def _finish_copy(self, total_copy):
        self.loading_screen.hide()
        self.show_confirmation_popup(f"Total copy {total_copy} logs")