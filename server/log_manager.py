import threading
import time
from typing import  Optional
import json
import os
from logs.global_log import GlobalLog
from logs.system_log import SystemLog
from logs.detection_log import DetectionLog, DetectionLogData
class LogManager:
    _instance: Optional['LogManager'] = None
    def __init__(self):
        if LogManager._instance is not None:
            raise RuntimeError("LogManager is a singleton, pleas use LogManager.instance() instead.")
        self.running = False
        self.global_log = None
        self.session_log = None
        self.system_log = None
        self.detection_log = None
    
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
        self.system_log = SystemLog(
            log_directory=log_directory,
            log_index=global_log_data.log_index, 
            max_file_size=global_log_data.max_file_size,
            update_index_callback=self.global_log.increment_log_index,
        )
        self.detection_log = DetectionLog(log_directory=log_directory)
        self.running = True
    
        self.system_log.start_session()
        self.thd = threading.Thread(target=self._run_periodic_updates, daemon=True)
        self.thd.start()

    def log_message(self, message: str):
        self.system_log.log_event(message=message)

    def save_detection(self, detection_data: DetectionLogData):
        self.detection_log.save_detection_data(detection_data)

    def update_calibration_data(self, threshold: int):
        self.global_log.update_calibration_data(threshold)

    def get_current_engine_time(self)->float:
        return round(self.global_log.global_data.total_run_minutes / 60, 1)

    def get_current_calibration_threshold(self)->int:
        if self.global_log.global_data.current_calibration.threshold is None:
            return 0
        return self.global_log.global_data.current_calibration.threshold

    def get_last_n_detections(self, num: int) -> list[DetectionLogData]:
        return self.detection_log.get_last_n_detections(num)

    def close(self):
        if self.thd:
            self.thd.join()

    