from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from screens.main_screen import MainScreen
from screens.logo_screen import LogoScreen 
from websocket.client import WebSocketClient
from config.config import ConfigManager
from screens.flip_screen_manager import FlippedScreenManager
from controller.idle_controller import IdleController

import asyncio
import sys
import os
import threading


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from share.wsmessage import *

from kivy.config import Config
Config.set('graphics', 'width', '320')  
Config.set('graphics', 'height', '240') 
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'dpi', '96')  

from kivy.core.window import Window
# Window.size = (640, 480)
#Window.fullscreen = True

def get_current_program_folder():
  return os.path.dirname(os.path.abspath(__file__))

class MetalDetectionApp(App):
    def build(self):
        if ConfigManager.instance().is_flip_screen():
            sm = FlippedScreenManager()
        else:
            sm = ScreenManager()

        self.joystick = None
        # Add LogoScreen first, then other screens
        self.logo_screen = LogoScreen(name="logo")
        self.main_screen = MainScreen(name="main")
        self.logo_screen.set_recover_func(
            callback=self.main_screen.get_stack_widget().show_popups_when_exit_idle
        )
        sm.add_widget(self.logo_screen) 
        sm.add_widget(self.main_screen)
        
        self.logo_screen.set_title(ConfigManager.instance().logo_tile)
        self.logo_screen.set_version(ConfigManager.instance().version)

        self.event_loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        if ConfigManager.instance().run_on_rpi():
            self.monitor_joystick()
            print("start monitor_joystick........")
        
        if ConfigManager.instance().is_support_keyboard():
            Window.bind(on_key_down=self.handle_keyboard)
            print("start listening keyboard input.")

        if ConfigManager.instance().is_enable_idle_checking():
            self.start_idle_handling()
            print("start idle handling thread.")

        self.start_websocket()
        return sm

    def _run_event_loop(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def monitor_joystick(self):
        from controller.joystick import JoyStick
        self.joystick = JoyStick(callback=self.handle_signal)
        if ConfigManager.instance().is_keypad_mode():
            self.joystick.setup(
                up=ConfigManager.instance().keypad_pins.up,
                down=ConfigManager.instance().keypad_pins.down,
                left=ConfigManager.instance().keypad_pins.left,
                right=ConfigManager.instance().keypad_pins.right,
                center=ConfigManager.instance().keypad_pins.center
            )
        else:
            self.joystick.setup(
                up=ConfigManager.instance().joystick_pins.up,
                down=ConfigManager.instance().joystick_pins.down,
                left=ConfigManager.instance().joystick_pins.left,
                right=ConfigManager.instance().joystick_pins.right,
                center=ConfigManager.instance().joystick_pins.center,
            )
        self.joystick.run()

    def _stop_joystick(self):
        if self.joystick is not None:
            self.joystick.stop()

    def stop(self):
        self._stop_joystick()

    def start_idle_handling(self):
        idle_seconds = ConfigManager.instance().idle_seconds
        self.idle_controller = IdleController(idle_seconds, self.switch_to_logo_screen)
        self.idle_controller.start()

    def _stop_idle_handling(self):
        if self.idle_controller is not None:
            self.idle_controller.stop()

    def switch_to_logo_screen(self):
        if self.root.current != "logo":
            self.root.current = "logo"
        self.main_screen.get_stack_widget().hide_popups_when_idle()

    def handle_signal(self, direction: str):
        print(f"Received direction signal: {direction}")
        if ConfigManager.instance().is_enable_idle_checking():
            self.idle_controller.update_clicked()

        current_screen = self.root.current
        if current_screen == "main":
            stack_widget = self.root.get_screen("main").ids.stack_widget     
            stack_widget.handle_direction(direction)
            skip_flag = False
            if stack_widget.is_analyzer():
                skip_flag = True
            
            if ConfigManager.instance().is_enable_idle_checking():
                self.idle_controller.set_skip_checking(is_skip=skip_flag)
        else:
            logo_screen = self.root.get_screen("logo")
            logo_screen.handle_direction(direction)
        print(f"Handle direction signal done: {direction}")

    
    def start_websocket(self):
        if not self.event_loop.is_running():
            raise RuntimeError("Event loop is not running.. make sure it running first")

        url = f"ws://{ConfigManager.instance().server_address}:{ConfigManager.instance().server_port}"
        WebSocketClient.instance().start(
            url=url,
            event_loop=self.event_loop,
            message_callback=self.main_screen.handle_websocket_messages,
            disconnect_callback=self.main_screen.handle_websocket_disconnect,
        )

    def on_stop(self):
        if self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        self.loop_thread.join()

    def handle_keyboard(self, window, key, *args):
        key_mapping = {
            273: "up",
            274: "down",
            276: "left",
            275: "right",
            13: "center"
        }

        if key in key_mapping:
            direction = key_mapping[key]
            print(f"Keyboard event detected: {direction}")
            self.handle_signal(direction)

if __name__ == "__main__":
    config_path = f"{get_current_program_folder()}/config/config.json"
    ConfigManager.instance().read_config(config_path)
    app = MetalDetectionApp()
    app.run()
    app.stop()

