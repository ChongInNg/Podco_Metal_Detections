from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from log.logger import Logger

Builder.load_file("kv/option_screen.kv")

class OptionScreen(Screen):
    title = StringProperty('Main Menu')
    current_button = StringProperty('')
    button_ids = ["detection_btn", "calibration_btn", "analyzer_btn", "setting_btn"]
    
    def on_kv_post(self, base_widget):
       self.reset_data()
       
    def reset_data(self):
        self.clear_focus()
        self.current_button = "detection_btn"
        self.ids[self.current_button].state = "down"

    def get_title(self):
        return self.title
    
    def set_focus(self, is_up: bool):
        if is_up:
            if self.current_button == "":
                self.current_button = self.button_ids[0]
                self.set_focus_button(self.current_button)
            else:
                current_index = self.button_ids.index(self.current_button)
                new_index = (current_index - 1) % len(self.button_ids)
                self.current_button = self.button_ids[new_index]
                self.set_focus_button(self.current_button)
        else:
            if self.current_button == "":
                self.current_button = self.button_ids[len(self.button_ids) - 1]
                self.set_focus_button(self.current_button)
            else:
                current_index = self.button_ids.index(self.current_button)
                new_index = (current_index + 1) % len(self.button_ids)
                self.current_button = self.button_ids[new_index]
                self.set_focus_button(self.current_button)

    def clear_focus(self):
        for button_id in self.button_ids:
            button = self.ids[button_id]
            button.state = "normal"

    def set_focus_button(self, focused_button_id):
        # Reset all buttons to "normal" state
        self.clear_focus()

        focused_button = self.ids[focused_button_id]
        focused_button.state = "down"

    def handle_on_enter(self):
        if self.current_button == "detection_btn":
            self.on_detection_btn_click()
        elif self.current_button == "calibration_btn":
            self.on_calibration_btn_click()
        elif self.current_button == "analyzer_btn":
            self.on_analyzer_btn_click()
        elif self.current_button == "setting_btn":
            self.on_setting_btn_click()
        else:
            Logger.debug("No button selected")
            
        self.clear_focus()
        self.current_button = ""

    def navigate_to_screen(self, screen_name):
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_screen_name(screen_name)
        Logger.debug(f"Navigating to {screen_name}")

    def on_detection_btn_click(self):
        self.navigate_to_screen("detection")

    def on_calibration_btn_click(self):
        self.navigate_to_screen("calibration")

    def on_analyzer_btn_click(self):
        self.navigate_to_screen("analyzer")

    def on_setting_btn_click(self):
        self.navigate_to_screen("setting")
        