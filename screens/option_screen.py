from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/option_screen.kv")

class OptionScreen(Screen):
    title = StringProperty('Main Menu')

    def set_focus(self, focused_button_id):
        # Reset all buttons to "normal" state
        for button_id in ["detection_btn", "calibration_btn", "analyzer_btn"]:
            button = self.ids[button_id]
            button.state = "normal"

        focused_button = self.ids[focused_button_id]
        focused_button.state = "down"

    def navigate_to_screen(self, screen_name):
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_screen_name(screen_name)
        print(f"Navigating to {screen_name}")

    def on_detection_btn_click(self):
        self.navigate_to_screen("detection")

    def on_calibration_btn_click(self):
        self.navigate_to_screen("calibration")

    def on_analyzer_btn_click(self):
        self.navigate_to_screen("analyzer")