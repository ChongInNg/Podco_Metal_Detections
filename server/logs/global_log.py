from datetime import datetime
from .base_log import BaseLog
from log.logger import Logger
from config.config import ConfigManager

class SessionLog:
    def __init__(self):
        self.started_at:datetime = None
        self.last_updated_at:datetime = None
        self.total_run_minutes = 0
        self.current_engine_minutes = 0

    def set_current_engine_minutes(self, engine_minutes: int):
        self.current_engine_minutes = engine_minutes

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
        self.current_engine_minutes = data.get("current_engine_minutes")
    
    def to_dict(self):
        return {
            "started_at": self.started_at.isoformat(),
            "last_updated_at": self.last_updated_at.isoformat(),
            "total_run_minutes": self.total_run_minutes,
            "current_engine_minutes": self.current_engine_minutes
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

class GlobalLogData:
    def __init__(self):
        self.total_run_minutes = 0
        self.orig_total_run_minutes = 0
        self.log_file_count = 0
        self.max_file_size = 1024 * 1024 * 100
        self.current_threshold = 1000
        self.session_histories = SessionLogHistory()
        self.current_session = SessionLog()

    def to_dict(self):
        return {
            "total_run_minutes": self.total_run_minutes,
            "current_threshold": self.current_threshold,
            "current_session": self.current_session.to_dict(),
            "session_histories": self.session_histories.to_dict(),
        }
    
    def update_run_time(self):
        self.current_session.update_run_time()
        self.total_run_minutes = self.orig_total_run_minutes + self.current_session.get_total_run_minutes()

    def init_data(self):
        self.current_session.init_data()

    def parse_data(self, data: dict):
        self.total_run_minutes = data.get("total_run_minutes")
        self.orig_total_run_minutes = self.total_run_minutes
        self.log_file_count = ConfigManager.instance().back_log_count
        self.max_file_size = ConfigManager.instance().back_log_size
        self.current_threshold = data.get("current_threshold")
        self.current_session.parse_data(data.get("current_session"))
        self.session_histories.parse_data(data.get("session_histories"))

        if self.log_file_count is None or self.log_file_count == 0:
            self.log_file_count = 10
    
class GlobalLog(BaseLog):
    def __init__(self, log_directory:str, file_name:str="global_log.json"):
        super().__init__(log_directory=log_directory, file_name=file_name)
        self.global_data = GlobalLogData()
        self._init_data()
    
    def update_global_log(self):
        self.global_data.update_run_time()
        self._write_json(self.global_data.to_dict())
        Logger.info("Global log updated.")

    def _init_data(self):
        global_log = self._read_json()
        if not global_log:
            self.global_data.init_data()
            self._write_json(self.global_data.to_dict())
        else:
            self.global_data.parse_data(global_log)
            # put current session log to the histories
            self.global_data.current_session.set_current_engine_minutes(self.global_data.orig_total_run_minutes)
            self.global_data.session_histories.add_session_log(self.global_data.current_session)
            self.global_data.current_session = SessionLog()
            self.global_data.current_session.init_data()
            self._write_json(self.global_data.to_dict())


    def get_global_log(self) -> GlobalLogData:
        return self.global_data