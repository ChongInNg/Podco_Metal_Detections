from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.main_screen import MainScreen
from screens.logo_screen import LogoScreen 
from websocket.client import WebSocketClient
from config.config import ConfigManager
from screens.flip_screen_manager import FlippedScreenManager
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
        if ConfigManager.instance().run_on_rpi():
            sm = FlippedScreenManager()
        else:
            sm = ScreenManager()

        self.joystick = None
        # Add LogoScreen first, then other screens
        self.logo_screen = LogoScreen(name="logo")
        self.main_screen = MainScreen(name="main")
        sm.add_widget(self.logo_screen) 
        sm.add_widget(self.main_screen)
        
        self.event_loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        if ConfigManager.instance().run_on_rpi():
            self.monitor_joystick()
            print("start monitor_joystick........")
        
        if ConfigManager.instance().is_support_keyboard():
            Window.bind(on_key_down=self.handle_keyboard)
            print("start listening keyboard input.")

        self.start_websocket()
        return sm

    def _run_event_loop(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def monitor_joystick(self):
        from controller.joystick import JoyStick
        self.joystick = JoyStick(callback=self.handle_signal)
        self.joystick.run()

    def stop_joystick(self):
        if self.joystick is not None:
            self.joystick.stop()

    def handle_signal(self, direction: str):
        print(f"Received direction signal: {direction}")

        app = App.get_running_app()

        current_screen = app.root.current
        if current_screen == "main":
            stack_widget = app.root.get_screen("main").ids.stack_widget     
            stack_widget.handle_direction(direction)
        else:
            logo_screen = app.root.get_screen("logo")
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
    app.stop_joystick()

