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


from kivy.config import Config
Config.set('graphics', 'width', '320')   # Your screen width
Config.set('graphics', 'height', '240')  # Your screen height
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'dpi', '96')  

# test
#Window.size = (640, 480)
#Window.fullscreen = True


from kivy.core.window import Window

class MetalDetectionApp(App):
    def build(self):
        sm = ScreenManager()
        print(f"1111111111 window size: {Window.size}") 
        # Add LogoScreen first, then other screens
        sm.add_widget(LogoScreen(name="logo")) 
        sm.add_widget(MainScreen(name="main"))
        
        self.monitor_joystick()
        return sm

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



if __name__ == "__main__":
    app = MetalDetectionApp()
    app.run()
    app.stop_joystick()

