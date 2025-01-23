from datetime import datetime
from .base_log import BaseLog
import os

class SystemLog(BaseLog):
    def __init__(self,log_directory:str, log_index, max_file_size, update_index_callback,  file_name="system_log"):
        file_full_name = f"{file_name}_{log_index}.log"
        super().__init__(log_directory=log_directory, file_name=file_full_name)
        self.log_index = log_index
        self.max_file_size = max_file_size
        self.update_index_callback = update_index_callback

    def start_session(self):
        self.log_event("Log Session Started")

    def log_event(self, message):
        if self._is_over_size():
            self._increase_index()

        with open(self.full_name, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"{timestamp} - {message}\n")

    def _is_over_size(self)->bool:
        if os.path.exists(self.full_name) and os.path.getsize(self.full_name) > self.max_file_size:
            return True
        return False
    
    def _increase_index(self):
        self.log_index += 1
        self.full_name = f"{self.file_name}_{self.log_index}.log"
        self.update_index_callback(self.log_index)
