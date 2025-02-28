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
            log_index=global_log_data.log_index, 
            max_file_size=global_log_data.max_file_size,
            update_index_callback=self.global_log.increment_log_index,
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

    def get_current_calibration_data(self)->CalibrationLogData:
        return self.calibration_log.get_current_calibration()
    
    def get_last_n_detections(self, num: int) -> list[DetectionLogData]:
        return self.detection_log.get_last_n_detections(num)

    def close(self):
        if self.thd:
            self.thd.join()

    