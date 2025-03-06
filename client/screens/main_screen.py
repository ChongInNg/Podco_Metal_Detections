from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.clock import Clock

import sys
import os
from screens.detection_screen import DetectionViewData
from screens.calibration_screen import CalibrationViewData
from screens.analyzer_screen import AnalyzerData
from screens.stack_widget import StackWidget
from screens.screen_header import ScreenHeader
from log.logger import Logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

Builder.load_file("kv/main_screen.kv")

class MainScreen(Screen):
    title = StringProperty("Main Menu")

    def get_stack_widget(self)->StackWidget:
        return self.ids.stack_widget
    
    def get_screen_header(self) -> ScreenHeader:
        return self.ids.screen_header
    
    def handle_websocket_disconnect(self):
        self.get_screen_header().update_server_status(False)
        Logger.warning(f"handle the websocket disconnect success.")
    
    def handle_websocket_messages(self, msg: BaseWsMessage):
        try:
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
            elif isinstance(msg, SetDefaultCalibrationResponse):
                self._handle_set_default_calibration_response(msg)
            elif isinstance(msg, GetLastNDetectionsResponse):
                self._handle_get_last_n_detections_response(msg)
            elif isinstance(msg, SetThresholdResponse):
                self._handle_set_threshold_response(msg)
            elif isinstance(msg, SystemErrorResponse):
                self._handle_system_error_response(msg)
            elif isinstance(msg, GetCalibrationResponse):
                self._get_calibration_response(msg)
            elif isinstance(msg, NotifyCalibrationFailedMessage):
                self._handle_calibration_failed(msg)
            else:
                Logger.error(f"Cannot handle this message: {msg}")
        except Exception as ex:
            import traceback
            traceback.print_stack()
            Logger.error(f"handle_websocket_messages failed. error: {ex}")

    def _handle_detection_data(self, msg: NotifyDetectionMessage) -> None:
        Clock.schedule_once(lambda dt: self.get_stack_widget().get_detection_screen().add_detection(
            DetectionViewData(
                T_Value=str(msg.t_value),
                D_Value=str(msg.d_value),
                CH1_N=str(msg.ch1_area_n),
                CH1_P=str(msg.ch1_area_p),
                CH2_N=str(msg.ch2_area_n),
                CH2_P=str(msg.ch2_area_p),
        )))

    def _handle_calibration_data(self, msg: NotifyCalibrationMessage) -> None:
        self.update_calibration_view(
             CalibrationViewData(
                T_Value=str(msg.t_value),
                D_Value=str(msg.d_value),
                CH1_N=str(msg.neg_threshold1),
                CH1_P=str(msg.pos_threshold1),
                CH1_M=str(msg.mid_ch1),
                CH2_N=str(msg.neg_threshold2),
                CH2_P=str(msg.pos_threshold2),
                CH2_M=str(msg.mid_ch2)
            )
        )

    def update_calibration_view(self, calibration_data: CalibrationViewData):
        Clock.schedule_once(
            lambda dt: self.get_stack_widget().get_calibration_screen().update_data(calibration_data),
        )

    def _handle_raw_data(self, msg: NotifyRawDataMessage) -> None:
        Clock.schedule_once(lambda dt: self.get_stack_widget().get_analyzer_screen().update_data(
            AnalyzerData(
                TimeStamp=msg.timestamp,
                Input1_Raw=msg.input1_raw,
                Input2_Raw=msg.input2_raw,
                CH1_N=msg.ch1_area_n,
                CH1_P=msg.ch1_area_p,
                CH2_N=msg.ch2_area_n,
                CH2_P=msg.ch2_area_p,
        )))

    def _handle_threshold_data(self, msg: NotifyThresholdAdjustedMessage) -> None:
        Clock.schedule_once(lambda dt: self.get_stack_widget().get_analyzer_screen().update_threshold(msg.area_threshold))
    
    def _handle_bypass_data(self, msg: NotifyByPassMessage) -> None:
        Clock.schedule_once(lambda dt: self.get_stack_widget().get_setting_screen().update_bypass(msg.bypass))
        Clock.schedule_once(lambda dt: self.get_stack_widget().get_analyzer_screen().update_bypass(msg.bypass))

    def _handle_registration_response(self, msg: RegistrationWsResponse) -> None:
        on_status = False 
        if msg.is_success():
            on_status = True
            Logger.debug(f"handle the registration response success.status: {on_status}")
        else:
            Logger.error(f"registration response is wrong.")
        Clock.schedule_once(lambda dt: self.get_screen_header().update_server_status(on_status))

    def _handle_set_default_calibration_response(self, msg: SetDefaultCalibrationResponse):
        Clock.schedule_once(lambda dt: 
            self.get_stack_widget().get_setting_screen().update_reset_factory_status(msg.is_success())
        )
        Logger.debug(f"handle the set default calibration response success. is_success: {msg.is_success()}")

    def _handle_set_threshold_response(self, msg: SetThresholdResponse):
        Clock.schedule_once(lambda dt: 
            self.get_stack_widget().get_analyzer_screen().update_set_threshold_status(msg.is_success())
        )
        Logger.debug(f"handle the set threshold response success. is_success: {msg.is_success()}")

    def _handle_get_last_n_detections_response(self, msg: GetLastNDetectionsResponse):
        if msg.is_success():
            Clock.schedule_once(lambda dt: self.get_stack_widget().get_detection_screen().init_detections(msg.detections))
        else:
            Logger.error(f"get last n detection response is not success, cannot handle in UI")
            # should popup error
    
    def _handle_system_error_response(self, msg: SystemErrorResponse):
        Logger.debug("Didn't handle sysstem error response now.")

    def _get_calibration_response(self, msg: GetCalibrationResponse):
        self.update_calibration_view(
             CalibrationViewData(
                T_Value=str(msg.calibration_data.t_value),
                D_Value=str(msg.calibration_data.d_value),
                CH1_N=str(msg.calibration_data.neg_threshold1),
                CH1_P=str(msg.calibration_data.pos_threshold1),
                CH1_M=str(msg.calibration_data.mid_ch1),
                CH2_N=str(msg.calibration_data.neg_threshold2),
                CH2_P=str(msg.calibration_data.pos_threshold2),
                CH2_M=str(msg.calibration_data.mid_ch2)
            )
        )
        current_threshold = msg.calibration_data.current_threshold
        current_bypass = msg.calibration_data.current_bypass
        analyzer_screen = self.get_stack_widget().get_analyzer_screen()
        Clock.schedule_once(lambda dt: analyzer_screen.update_threshold(current_threshold))
        Clock.schedule_once(lambda dt: analyzer_screen.update_bypass(current_bypass))

    def _handle_calibration_failed(self, msg: NotifyCalibrationFailedMessage):
        Clock.schedule_once(lambda dt: self.get_stack_widget().show_calibration_failed_popup(msg.reason))
        Logger.debug(f"_handle_calibration_failed success. reason: {msg.reason}")

