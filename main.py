from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from screens.main_screen import MainScreen
from screens.detection_screen import DetectionScreen
from screens.calibration_screen import CalibrationScreen
from screens.analyzer_screen import AnalyzerScreen

from kivy.config import Config
Config.set('graphics', 'width', '320')   # Your screen width
Config.set('graphics', 'height', '240')  # Your screen height
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'dpi', '96')  

class MetalDetectionApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(DetectionScreen(name="detection"))
        sm.add_widget(CalibrationScreen(name="calibration"))
        sm.add_widget(AnalyzerScreen(name="analyzer"))
        return sm

if __name__ == "__main__":
    MetalDetectionApp().run()
