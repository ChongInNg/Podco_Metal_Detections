from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/stack_widget.kv")

class StackWidget(Screen):
    current_screen = StringProperty('')

    def change_screen(self, screen_name):
        self.ids.stack_manager.current = screen_name
        self.current_screen = screen_name

        app = App.get_running_app()
        main_screen = app.root.get_screen("main")
        screen_header = main_screen.ids.screen_header
        if self.is_detection():
            screen_header.update_header(title="Detections")
        elif self.is_calibration():
            screen_header.update_header(title="Calibrations")
        elif self.is_analyzer():
            screen_header.update_header(title="Analyzer")
        elif self.is_option():
            screen_header.update_header(title="Main Menu")


    def is_detection(self):
        return self.current_screen == "detection"
    
    def is_calibration(self):
        return self.current_screen == "calibration"
    
    def is_analyzer(self):
        return self.current_screen == "analyzer"
    
    def is_option(self):
        return self.current_screen == "option"