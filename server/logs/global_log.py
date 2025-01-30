from datetime import datetime
from .base_log import BaseLog
from log.logger import Logger

class SessionLog:
    def __init__(self):
        self.started_at:datetime = None
        self.last_updated_at:datetime = None
        self.total_run_minutes = 0

    def init_data(self):
        self.started_at = datetime.now()
        self.last_updated_at = datetime.now()
        self.total_run_minutes = 0
    
    def update_run_time(self):
        self.last_updated_at = datetime.now()
        self.total_run_minutes = (int)((self.last_updated_at - self.started_at).total_seconds() // 60)
    
    def get_total_run_minutes(self)->int:
        return self.total_run_minutes
    
    def parse_data(self, data: dict):
        self.started_at = datetime.fromisoformat(data.get("started_at"))
        self.last_updated_at = datetime.fromisoformat(data.get("last_updated_at"))
        self.total_run_minutes = data.get("total_run_minutes")
    
    def to_dict(self):
        return {
            "started_at": self.started_at.isoformat(),
            "last_updated_at": self.last_updated_at.isoformat(),
            "total_run_minutes": self.total_run_minutes
        }

class SessionLogHistory:
    def __init__(self):
        self.sessions:list[SessionLog] = []

    def add_session_log(self, session_log: SessionLog):
        self.sessions.append(session_log)

    def to_dict(self):
        return [item.to_dict() for item in self.sessions]
    
    def parse_data(self, data: list):
        for item in data:
            session_log = SessionLog()
            session_log.parse_data(item)
            self.sessions.append(session_log)

class CalibrationLog:
    def __init__(self):
        self.started_at:datetime = None
        self.last_updated_at:datetime = None
        self.total_run_minutes = 0
        self.orig_total_run_minutes = 0
        self.threshold = 0

    def update_run_time(self, total_run_minutes: int):
        if self.started_at is not None:
            self.last_updated_at = datetime.now()
            self.total_run_minutes = self.orig_total_run_minutes + total_run_minutes
        
    def set_calibration_data(self, threshold: int):
        self.started_at = datetime.now()
        self.last_updated_at = datetime.now()
        self.total_run_minutes = 0
        self.threshold = threshold

    def parse_data(self, data: dict):
        if data.get("started_at") is not None:
            self.started_at = datetime.fromisoformat(data.get("started_at"))
        
        if data.get("last_updated_at") is not None:
            self.last_updated_at = datetime.fromisoformat(data.get("last_updated_at"))
        
        self.total_run_minutes = data.get("total_run_minutes")
        self.orig_total_run_minutes = self.total_run_minutes
        self.threshold = data.get("threshold")

    def to_dict(self):
        str_started_at:str = None
        if self.started_at is not None:
            str_started_at = self.started_at.isoformat()
        str_last_updated_at:str = None
        if self.last_updated_at is not None:
            str_last_updated_at = self.last_updated_at.isoformat()
        return {
            "started_at": str_started_at,
            "last_updated_at": str_last_updated_at,
            "total_run_minutes": self.total_run_minutes,
            "threshold": self.threshold
        }
    
class CalibrationHistory:
    def __init__(self):
        self.calibrations:list[CalibrationLog] = []

    def add_calibration_log(self, calibration_log: CalibrationLog):
        self.calibrations.append(calibration_log)

    def parse_data(self, data: list):
         for item in data:
            cali_log = CalibrationLog()
            cali_log.parse_data(item)
            self.calibrations.append(cali_log)

    def to_dict(self):
        return [item.to_dict() for item in self.calibrations]
    
class GlobalLogData:
    def __init__(self):
        self.total_run_minutes = 0
        self.orig_total_run_minutes = 0
        self.log_index = 0
        self.max_file_size = 1024 * 1024 * 100
        self.session_histories = SessionLogHistory()
        self.current_session = SessionLog()
        self.calibration_histories = CalibrationHistory()
        self.current_calibration = CalibrationLog()

    def to_dict(self):
        return {
            "total_run_minutes": self.total_run_minutes,
            "log_index": self.log_index,
            "max_file_size": self.max_file_size,
            "current_session": self.current_session.to_dict(),
            "current_calibration": self.current_calibration.to_dict(),
            "session_histories": self.session_histories.to_dict(),
            "calibration_histories": self.calibration_histories.to_dict()
        }
    
    def update_run_time(self):
        self.current_session.update_run_time()
        self.total_run_minutes = self.orig_total_run_minutes + self.current_session.get_total_run_minutes()
        self.current_calibration.update_run_time(self.current_session.get_total_run_minutes())

    def init_data(self):
        self.current_session.init_data()

    def parse_data(self, data: dict):
        self.total_run_minutes = data.get("total_run_minutes")
        self.orig_total_run_minutes = self.total_run_minutes
        self.log_index = data.get("log_index")
        self.max_file_size = data.get("max_file_size")
        self.current_session.parse_data(data.get("current_session"))
        self.current_calibration.parse_data(data.get("current_calibration"))
        self.session_histories.parse_data(data.get("session_histories"))
        self.calibration_histories.parse_data(data.get("calibration_histories"))
    
class GlobalLog(BaseLog):
    def __init__(self, log_directory:str, file_name:str="global_log.json"):
        super().__init__(log_directory=log_directory, file_name=file_name)
        self.global_data = GlobalLogData()
        self._init_data()
    
    def update_global_log(self):
        self.global_data.update_run_time()
        self._write_json(self.global_data.to_dict())
        Logger.instance().info("Global log updated.")

    def _init_data(self):
        global_log = self._read_json()
        if not global_log:
            self.global_data.init_data()
            self._write_json(self.global_data.to_dict())
        else:
            self.global_data.parse_data(global_log)
            # put current session log to the histories
            self.global_data.session_histories.add_session_log(self.global_data.current_session)
            self.global_data.current_session = SessionLog()
            self.global_data.current_session.init_data()
            self._write_json(self.global_data.to_dict())

    def increment_log_index(self, index: int):
        self.global_data.log_index = index
        self._write_json(self.file_name, self.global_data.to_dict())

    def get_global_log(self) -> GlobalLogData:
        return self.global_data
