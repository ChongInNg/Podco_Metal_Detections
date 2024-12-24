from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/stack_widget.kv")

class StackWidget(Screen):
    def change_screen(self, screen_name):
        self.ids.stack_manager.current = screen_name

        app = App.get_running_app()
        main_screen = app.root.get_screen("main")
        screen_header = main_screen.ids.screen_header
        if screen_name == "detection":
            screen_header.update_header(title="Detections", show_back=True)
        elif screen_name == "calibration":
            screen_header.update_header(title="Calibrations", show_back=True)
        elif screen_name == "analyzer":
            screen_header.update_header(title="Analyzer", show_back=True)
        elif screen_name == "option":
            screen_header.update_header(title="Main Menu", show_back=False)