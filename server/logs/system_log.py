from datetime import datetime
from .base_log import BaseLog
import os

class SystemLog(BaseLog):
    def __init__(self, log_index, max_file_size, update_index_callback,  file_name="system_log"):
        full_name = f"{file_name}_{log_index}"
        super().__init__(file_name=full_name)
        self.log_index = log_index
        self.max_file_size = max_file_size
        self.update_index_callback = update_index_callback

    def start_session(self):
        self.log_event("Log Session Started")

    def log_event(self, message):
        if self._is_over_size():
            self._increase_index()

        system_log = self._read_json()
        system_log.setdefault("events", [])
        system_log["events"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
        })
        self._write_json(system_log)

    def _is_over_size(self)->bool:
        if os.path.exists(self.file_name) and os.path.getsize(self.file_name) > self.max_file_size:
            return True
        return False
    
    def _increase_index(self):
        self.log_index += 1
        self.file_name = f"{self.file_name}_{self.log_index}"
        self.update_index_callback(self.log_index)
