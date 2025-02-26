import json

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

from screens.option_screen import OptionScreen
from screens.detection_screen import DetectionScreen
from screens.calibration_screen import CalibrationScreen
from screens.analyzer_screen import AnalyzerScreen
from screens.screen_header import ScreenHeader
from screens.setting_screen import SettingScreen
from screens.common_popup import CommonPopup

Builder.load_file("kv/stack_widget.kv")

class StackWidget(Screen):
    current_screen = StringProperty('option')

    def handle_direction(self, direction):
        if direction == "left":
            if self.is_detection():
                self.change_to_option_screen()
            elif self.is_calibration():
                self.change_to_detection_screen()
            elif self.is_analyzer():
                analyzer_screen = self.get_analyzer_screen()
                is_handled = analyzer_screen.on_left_pressed()
                if is_handled:
                    print("Already handle, no need to handle in stackwidget")
                else:
                    self.change_to_calibration_screen()
            elif self.is_setting():
                setting_screen = self.get_setting_screen()
                setting_screen.on_left_pressed()
            else:
                print(f"Not support left direction in this screen: {self.current_screen}")
        elif direction == "right":
            if self.is_detection():
                self.change_to_calibration_screen()
            elif self.is_calibration():
                self.change_to_analyzer_screen()
            elif self.is_analyzer():
                analyzer_screen = self.get_analyzer_screen()
                is_handled = analyzer_screen.on_right_pressed()
                if is_handled:
                    print("Already handle, no need to handle in stackwidget")
                else:
                    self.change_to_option_screen()
            elif self.is_setting():
                setting_screen = self.get_setting_screen()
                setting_screen.on_right_pressed()
            else:
                print(f"Not support left direction in this screen: {self.current_screen}")

        elif direction == "up":
            if self.is_option():
                option_screen = self.get_option_screen()
                option_screen.set_focus(is_up = True)
            elif self.is_detection():
                detection_screen = self.get_detection_screen()
                detection_screen.on_up_pressed()
            elif self.is_analyzer():
                analyzer_screen = self.get_analyzer_screen()
                analyzer_screen.on_up_pressed()
            elif self.is_setting():
                setting_screen = self.get_setting_screen()
                setting_screen.on_up_pressed()
            else:
                print(f"Not support up direction in this screen: {self.current_screen}")

        elif direction == "down":
            if self.is_option():
                option_screen = self.get_option_screen()
                option_screen.set_focus(is_up = False)
            elif self.is_detection():
                detection_screen = self.get_detection_screen()
                detection_screen.on_down_pressed()
            elif self.is_analyzer():
                analyzer_screen = self.get_analyzer_screen()
                analyzer_screen.on_down_pressed()
            elif self.is_setting():
                setting_screen = self.get_setting_screen()
                setting_screen.on_down_pressed()
            else:
                print(f"Not support down direction in this screen: {self.current_screen}")

        elif direction == "center":
            if self.is_option():
                option_screen = self.get_option_screen()
                option_screen.handle_on_enter()
            elif self.is_analyzer():
                analyzer_screen = self.get_analyzer_screen()
                analyzer_screen.handle_on_enter()
            elif self.is_setting():
                setting_screen = self.get_setting_screen()
                setting_screen.handle_on_enter()
            else:
                print(f"Not support center direction in this screen: {self.current_screen}")
        else:
            print(f"Not support direction: {direction}")


    def change_to_screen_name(self, screen_name):
        if self.is_analyzer():
            # need to stop the analyzer thread first before switching to another screen
            screen = self.get_analyzer_screen()
            screen.stop()
            print(f"Stop the analyzer thread before switching to another screen: {screen_name}")

        self.ids.stack_manager.current = screen_name
        self.current_screen = screen_name
        title = ""
        if self.is_detection():
            screen = self.get_detection_screen()
            title = screen.get_title()
            screen.reset_data()
        elif self.is_calibration():
            screen = self.get_calibration_screen()
            title = screen.get_title()
            screen.reset_data()
        elif self.is_analyzer():
            screen = self.get_analyzer_screen()
            title = screen.get_title()
            screen.reset_data()
        elif self.is_option():
            screen = self.get_option_screen()
            title = screen.get_title()
            screen.reset_data()
        elif self.is_setting():
            screen = self.get_setting_screen()
            title = screen.get_title()
        self.get_screen_header().update_header(title)

    def change_to_option_screen(self):
        self.change_to_screen_name("option")
    
    def change_to_detection_screen(self):
        self.change_to_screen_name("detection")
    
    def change_to_calibration_screen(self):
        self.change_to_screen_name("calibration")

    def change_to_analyzer_screen(self):
        self.change_to_screen_name("analyzer")

    def is_detection(self) -> bool:
        return self.current_screen == "detection"
    
    def is_calibration(self) -> bool:
        return self.current_screen == "calibration"
    
    def is_analyzer(self) -> bool:
        return self.current_screen == "analyzer"
    
    def is_option(self) -> bool:
        return self.current_screen == "option"
    
    def is_setting(self) -> bool:
        return self.current_screen == "setting"
    
    def get_option_screen(self) -> OptionScreen:
        return self.ids.stack_manager.get_screen("option")
    
    def get_detection_screen(self)-> DetectionScreen:
        return self.ids.stack_manager.get_screen("detection")
    
    def get_calibration_screen (self)-> CalibrationScreen:
        return self.ids.stack_manager.get_screen("calibration")
    
    def get_analyzer_screen(self)-> AnalyzerScreen:
        return self.ids.stack_manager.get_screen("analyzer")
    
    def get_setting_screen(self)-> SettingScreen:
        return self.ids.stack_manager.get_screen("setting")

    def get_screen_header(self)-> ScreenHeader:
        app = App.get_running_app()
        main_screen = app.root.get_screen("main")
        return main_screen.ids.screen_header
    
    def show_calibration_failed_popup(self, reason: int):
        self.common_popup = CommonPopup()
        self.common_popup.update_title("Calibration Failed")
        reason_str = ""
        if reason == 1:
            reason_str = "Sequence Failed."
        elif reason == 2:
            reason_str = "Signal Failed."
        else:
            reason_str = "Unknow error."
        self.common_popup.update_message(f"Reason: {reason_str}")
        self.common_popup.handle_open()
    
    