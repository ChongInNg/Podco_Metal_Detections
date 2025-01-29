import json

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.clock import Clock
from screens.option_screen import OptionScreen
from screens.detection_screen import DetectionScreen, DetectionData
from screens.calibration_screen import CalibrationScreen, CalibrationData
from screens.analyzer_screen import AnalyzerScreen
from screens.screen_header import ScreenHeader
from websocket.message import *

Builder.load_file("kv/stack_widget.kv")

class StackWidget(Screen):
    current_screen = StringProperty('option')

    def change_screen(self, direction):
        if direction == "left":
            if self.is_detection():
                self.change_to_option_screen()
            elif self.is_calibration():
                self.change_to_detection_screen()
            elif self.is_analyzer():
                self.change_to_calibration_screen()
            else:
                print(f"Not support left direction in this screen: {self.current_screen}")
        elif direction == "right":
            if self.is_detection():
                self.change_to_calibration_screen()
            elif self.is_calibration():
                self.change_to_analyzer_screen()
            elif self.is_analyzer():
                self.change_to_option_screen()
            else:
                print(f"Not support left direction in this screen: {self.current_screen}")

        elif direction == "up":
            if self.is_option():
                option_screen = self.get_option_screen()
                option_screen.set_focus(is_up = True)
            elif self.is_detection():
                detection_screen = self.get_detection_screen()
                detection_screen.on_up_pressed()
            else:
                print(f"Not support up direction in this screen: {self.current_screen}")

        elif direction == "down":
            if self.is_option():
                option_screen = self.get_option_screen()
                option_screen.set_focus(is_up = False)
            elif self.is_detection():
                detection_screen = self.get_detection_screen()
                detection_screen.on_down_pressed()
            else:
                print(f"Not support down direction in this screen: {self.current_screen}")

        elif direction == "center":
            if self.is_option():
                option_screen = self.get_option_screen()
                option_screen.handle_enter()
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

    def is_detection(self):
        return self.current_screen == "detection"
    
    def is_calibration(self):
        return self.current_screen == "calibration"
    
    def is_analyzer(self):
        return self.current_screen == "analyzer"
    
    def is_option(self):
        return self.current_screen == "option"
    
    def is_setting(self):
        return self.current_screen == "setting"
    
    def get_option_screen(self) -> OptionScreen:
        return self.ids.stack_manager.get_screen("option")
    
    def get_detection_screen(self)-> DetectionScreen:
        return self.ids.stack_manager.get_screen("detection")
    
    def get_calibration_screen (self)-> CalibrationScreen:
        return self.ids.stack_manager.get_screen("calibration")
    
    def get_analyzer_screen(self)-> AnalyzerScreen:
        return self.ids.stack_manager.get_screen("analyzer")
    
    def get_setting_screen(self)-> AnalyzerScreen:
        return self.ids.stack_manager.get_screen("setting")

    def get_screen_header(self)-> ScreenHeader:
        app = App.get_running_app()
        main_screen = app.root.get_screen("main")
        return main_screen.ids.screen_header
    
    def handle_websocket_messages(self, message: str):
        try:
            msg_dict = json.loads(message)
            print(f"Decode message success: {msg_dict}\n")
            msg = BaseWsMessage.from_dict(msg_dict)
            print(f"msg1111111111: {msg.to_dict()}")
            if isinstance(msg, NotifyByPassMessage):
                self._handle_bypass_data(msg)
            elif isinstance(msg, NotifyCalibrationMessage):
                self._handle_calibration_data(msg)
            elif isinstance(msg, NotifyDetectionMessage):
                self._handle_detection_data(msg)
            elif isinstance(msg, NotifyRawDataMessage):
                self._handle_raw_data(msg)
            elif isinstance(msg, NotifyThresholdAdjustedMessage):
                self._handle_threshold_data(msg)
            elif isinstance(msg, RegistrationWsResponse):
                self._handle_registration_response(msg)
            else:
                print(f"Cannot handle this message: {msg}\n")
        except Exception as ex:
            print(f"parse json failed. error: {ex}\n")

    def _handle_detection_data(self, msg: NotifyDetectionMessage) -> None:
        Clock.schedule_once(lambda dt: self.get_detection_screen().add_detection(
            DetectionData(
                T_Value="20.1",
                D_Value="1000",
                CH1_N=str(msg.ch1_area_n),
                CH1_P=str(msg.ch1_area_p),
                CH2_N=str(msg.ch2_area_n),
                CH2_P=str(msg.ch2_area_p),
        )))

    def _handle_calibration_data(self, msg: NotifyCalibrationMessage) -> None:
        Clock.schedule_once(lambda dt: self.get_calibration_screen().update_data(
            CalibrationData(
                T_Value="20.1",
                D_Value="1000",
                CH1_N=str(msg.neg_threshold1),
                CH1_P=str(msg.pos_threshold1),
                CH1_M=str(msg.mid_ch1),
                CH2_N=str(msg.neg_threshold2),
                CH2_P=str(msg.pos_threshold2),
                CH2_M=str(msg.mid_ch2)
        )))

    def _handle_raw_data(self, msg: NotifyRawDataMessage) -> None:
        pass

    def _handle_threshold_data(self, msg: NotifyThresholdAdjustedMessage) -> None:
        pass
    
    def _handle_bypass_data(self, msg: NotifyByPassMessage) -> None:
        pass

    def _handle_registration_response(self, msg: RegistrationWsResponse) -> None:
        pass