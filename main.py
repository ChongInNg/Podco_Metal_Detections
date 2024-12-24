from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder

from screens.screen_header import ScreenHeader
from screens.main_screen import MainScreen
from screens.detection_screen import DetectionScreen
from screens.calibration_screen import CalibrationScreen
from screens.analyzer_screen import AnalyzerScreen
from screens.logo_screen import LogoScreen 


from kivy.config import Config
Config.set('graphics', 'width', '320')   # Your screen width
Config.set('graphics', 'height', '240')  # Your screen height
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'dpi', '96')  

# test
Window.size = (320, 240)
# Window.fullscreen = "auto"
class MetalDetectionApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Add LogoScreen first, then other screens
        sm.add_widget(LogoScreen(name="logo"))  # LogoScreen should be shown first
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(DetectionScreen(name="detection"))
        sm.add_widget(CalibrationScreen(name="calibration"))
        sm.add_widget(AnalyzerScreen(name="analyzer"))
        
        return sm

if __name__ == "__main__":
    MetalDetectionApp().run()
