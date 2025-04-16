import threading
import time
from typing import  Optional
import json
import os
from logs.global_log import GlobalLog
from logs.command_log import CommandLog
from logs.detection_log import DetectionLog, DetectionLogData
from logs.calibration_log import CalibrationLog, CalibrationLogData

class LogManager:
    _instance: Optional['LogManager'] = None
    def __init__(self):
        if LogManager._instance is not None:
            raise RuntimeError("LogManager is a singleton, pleas use LogManager.instance() instead.")
        self.running = False
        self.global_log = None
        self.session_log = None
        self.command_log = None
        self.detection_log: DetectionLog = None
        self.calibration_log: CalibrationLog = None

        self.current_pass = 0 # save current pass when the client isn't started
        self._is_calibration_failed = False
        self._calibration_failed_reason = -1

    @classmethod
    def instance(cls) -> 'LogManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _run_periodic_updates(self):
        while self.running:
            time.sleep(60)
            self.global_log.update_global_log()

    def setup(self, log_directory: str="./"):
        self.global_log = GlobalLog(log_directory=log_directory)
        global_log_data = self.global_log.get_global_log()
        self.command_log = CommandLog(
            log_directory=log_directory,
            max_file_size=global_log_data.max_file_size,
            log_file_count=global_log_data.log_file_count, 
        )
        self.detection_log = DetectionLog(log_directory=log_directory)
        self.calibration_log = CalibrationLog(log_directory=log_directory)
        self.running = True
    
        self.command_log.start_session()
        self.thd = threading.Thread(target=self._run_periodic_updates, daemon=True)
        self.thd.start()

    def log_command(self, message: str):
        self.command_log.log_event(message=message)

    def save_detection(self, detection_data: DetectionLogData):
        self.detection_log.save_detection_data(detection_data)

    def update_calibration_data(self, calibration_data: CalibrationLogData):
        self.calibration_log.update_calibration_log_data(calibration_data)

    def get_current_engine_time(self)->float:
        return round(self.global_log.global_data.total_run_minutes / 60, 1)
    
    def get_current_voltage(self)->float:
        return self.global_log.global_data.current_voltage

    def get_current_calibration_data(self)->CalibrationLogData:
        return self.calibration_log.get_current_calibration()
    
    def get_last_n_detections(self, num: int) -> list[DetectionLogData]:
        return self.detection_log.get_last_n_detections(num)

    def close(self):
        if self.thd:
            self.thd.join()

    def get_current_threshold(self)->int:
        return self.global_log.global_data.current_threshold
    
    def set_current_threshold(self, threshold: int):
        self.global_log.global_data.current_threshold = threshold

    def set_current_voltage(self, voltage: int):
        self.global_log.global_data.update_voltage(voltage)

    def set_current_bypass(self, bypass: int):
        self.current_pass = bypass

    def get_current_bypass(self)->int:
        return self.current_pass
    
    def is_calibration_failed(self)->bool:
        return self._is_calibration_failed
    
    def get_calibration_failed_reason(self)->int:
        return self._calibration_failed_reason
    
    def set_calibration_failed_reason(self, reason: int):
        self._is_calibration_failed = True
        self._calibration_failed_reason = reason
