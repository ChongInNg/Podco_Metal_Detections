from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from screens.screen_header import ScreenHeader
from screens.detection_screen import DetectionScreen
from screens.calibration_screen import CalibrationScreen
from screens.analyzer_screen import AnalyzerScreen
from screens.setting_screen import SettingScreen
from screens.option_screen import OptionScreen
from screens.stack_widget import StackWidget
from screens.main_screen import MainScreen
from screens.logo_screen import LogoScreen 
from websocket.client import WebSocketClient
import asyncio
import sys
import os
import threading
import time

# Dynamically add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the shared file
from share.wsmessage import *

from kivy.config import Config
Config.set('graphics', 'width', '320')  
Config.set('graphics', 'height', '240') 
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'dpi', '96')  

# test



# from kivy.core.window import Window
# Window.size = (640, 480)
#Window.fullscreen = True
class MetalDetectionApp(App):
    def build(self):
        sm = ScreenManager()
        # print(f"Current window size: {Window.size}") 

        self.joystick = None
        # Add LogoScreen first, then other screens
        self.logo_screen = LogoScreen(name="logo")
        self.main_screen = MainScreen(name="main")
        sm.add_widget(self.logo_screen) 
        sm.add_widget(self.main_screen)
        
        self.event_loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        # self.monitor_joystick()
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
            stack_widget.change_screen(direction)
        else:
            logo_screen = app.root.get_screen("logo")
            logo_screen.handle_direction(direction)
        print(f"Handle direction signal done: {direction}")


    def start_websocket(self):
        if not self.event_loop.is_running():
            raise RuntimeError("Event loop is not running.. make sure it running first")
       
        WebSocketClient.instance().start(
            url="ws://127.0.0.1:8765",
            event_loop=self.event_loop,
            message_callback=self.main_screen.handle_websocket_messages,
            disconnect_callback=self.main_screen.handle_websocket_disconnect,
        )

    def on_stop(self):
        if self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        self.loop_thread.join()

if __name__ == "__main__":
    app = MetalDetectionApp()
    BaseWsMessage(Header("", ""))
    
    app.run()
    app.stop_joystick()

