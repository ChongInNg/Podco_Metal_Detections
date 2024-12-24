from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder

from screens.screen_header import ScreenHeader
from screens.detection_screen import DetectionScreen
from screens.calibration_screen import CalibrationScreen
from screens.analyzer_screen import AnalyzerScreen
from screens.option_screen import OptionScreen
from screens.stack_widget import StackWidget
from screens.main_screen import MainScreen

from screens.logo_screen import LogoScreen 


from kivy.config import Config
Config.set('graphics', 'width', '320')   # Your screen width
Config.set('graphics', 'height', '240')  # Your screen height
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'dpi', '96')  

# test
Window.size = (320, 240)
Window.fullscreen = "auto"


class MetalDetectionApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Add LogoScreen first, then other screens
        sm.add_widget(LogoScreen(name="logo"))  # LogoScreen should be shown first
        sm.add_widget(MainScreen(name="main"))
        
        # self.monitor_joystick()
        return sm

    def monitor_joystick(self):
        from controller.joystick import JoyStick
        joystick = JoyStick(callback=self.handle_signal)
        joystick.run()

    def handle_signal(self, direction: str):
        print(f"Received direction signal: {direction}")

        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_screen(direction)
        print(f"Handle direction signal done: {direction}")



if __name__ == "__main__":
    MetalDetectionApp().run()
