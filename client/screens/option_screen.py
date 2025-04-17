from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty,BooleanProperty
from kivy.lang import Builder
from log.logger import Logger
from controller.role_manager import RoleManager

Builder.load_file("kv/option_screen.kv")

class OptionScreen(Screen):
    title = StringProperty('Main Menu')
    current_button = StringProperty('')
    analyzer_hidden = BooleanProperty(True)
    exit_hidden = BooleanProperty(True)
    setting_hidden = BooleanProperty(False)
    detection_hidden = BooleanProperty(False)
    calibration_hidden = BooleanProperty(False)

    admin_button_ids = ["detection_btn", "calibration_btn", 
                "analyzer_btn", "status_btn", "setting_btn", "exit_btn"]
    
    user_button_ids = ["detection_btn", "calibration_btn",  "status_btn",
                "setting_btn", "exit_btn"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_ids = OptionScreen.user_button_ids

    def on_kv_post(self, base_widget):
        self.reset_data()
        self._hide_analyzer_option()
        self._hide_exit_option()
 
    def reset_data(self):
        self.current_button = "detection_btn"
        self.set_focus_button(self.current_button)
        self.reset_ui_visiblities()

    def get_title(self):
        return self.title
    
    def set_focus(self, is_up: bool):
        if is_up:
            current_index = self.button_ids.index(self.current_button)
            new_index = (current_index - 1) % len(self.button_ids)
            self.current_button = self.button_ids[new_index]
            self.set_focus_button(self.current_button)
        else: #down
            current_index = self.button_ids.index(self.current_button)
            new_index = (current_index + 1) % len(self.button_ids)
            self.current_button = self.button_ids[new_index]
            self.set_focus_button(self.current_button)

        self.reset_ui_visiblities()
                
    
    def reset_ui_visiblities(self):
        if RoleManager.instance().is_admin():
            if self.current_button == "detection_btn":
                self._hide_exit_option()
                self._hide_setting_option()
                self._show_detection_option()
                self._show_calibration_option()
                self._show_analyzer_option()
            elif self.current_button == "status_btn":
                self._hide_exit_option()
                self._hide_detection_option()
                self._show_setting_option()
                self._show_calibration_option()
            elif self.current_button == "exit_btn":
                self._show_exit_option()
                self._show_setting_option()
                self._hide_detection_option()
                self._hide_calibration_option()
        else:
            if self.current_button == "detection_btn":
                self._hide_exit_option()
                self._show_detection_option()
            elif self.current_button == "exit_btn":
                self._show_exit_option()
                self._hide_detection_option()

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
        elif self.current_button == "status_btn":
            self.on_status_btn_click()
        elif self.current_button == "exit_btn":
            self.on_exit_btn_click()
        else:
            Logger.debug("No button selected")
            self.clear_focus()

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

    def on_status_btn_click(self):
         self.navigate_to_screen("status")

    def on_exit_btn_click(self):
        App.get_running_app().switch_to_logo_screen()
        self._hide_analyzer_option()
        self.reset_data()

    def _hide_analyzer_option(self):
        self.analyzer_hidden = True
        self.ids.analyzer_layout.opacity = 0

    def _show_analyzer_option(self):
        self.analyzer_hidden = False
        self.ids.analyzer_layout.opacity = 1

    def _hide_detection_option(self):
        self.detection_hidden = True
        self.ids.detection_layout.opacity = 0

    def _show_detection_option(self):
        self.detection_hidden = False
        self.ids.detection_layout.opacity = 1

    def _hide_exit_option(self):
        self.exit_hidden = True
        self.ids.exit_layout.opacity = 0

    def _show_exit_option(self):
        self.exit_hidden = False
        self.ids.exit_layout.opacity = 1

    def _hide_setting_option(self):
        self.setting_hidden = True
        self.ids.setting_layout.opacity = 0

    def _show_setting_option(self):
        self.setting_hidden = False
        self.ids.setting_layout.opacity = 1

    def _hide_calibration_option(self):
        self.calibration_hidden = True
        self.ids.calibration_layout.opacity = 0

    def _show_calibration_option(self):
        self.calibration_hidden = False
        self.ids.calibration_layout.opacity = 1

    def update_ui_when_admin_login(self):
        self._show_analyzer_option()
        self._hide_exit_option()
        self._hide_setting_option()
        self._show_detection_option()
        self._show_calibration_option()
        self.button_ids = OptionScreen.admin_button_ids

    def update_ui_when_user_login(self):
        self._hide_analyzer_option()
        self._hide_exit_option()

        self._show_detection_option()
        self._show_calibration_option()
        self._show_setting_option()
        self.button_ids = OptionScreen.user_button_ids

