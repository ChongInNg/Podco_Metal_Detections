from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from screens.main_screen import MainScreen
from screens.detection_screen import DetectionScreen
from screens.calibration_screen import CalibrationScreen
from screens.analyzer_screen import AnalyzerScreen

# Set the screen resolution to fit a 2.4-inch display
Window.size = (320, 240)

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
