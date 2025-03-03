from .base_log import BaseLog
import os
from datetime import datetime
from log.logger import Logger

class CommandLog(BaseLog):
    def __init__(self,log_directory:str, max_file_size, log_file_count: int, file_name="command.log"):
        super().__init__(log_directory=log_directory, file_name=file_name)
        self.max_file_size = max_file_size
        self.log_file_count = log_file_count

    def start_session(self):
        self.log_event("Log Session Started")

    def log_event(self, message):
        try:
            self._write_message(message)
        except IOError as e:
            Logger.error(f"Error writing to system log file: {e}")

    def _write_message(self, message: str):
        # no need to lock: only one thread will write, better for performenance
        if os.path.exists(self.full_name) and os.path.getsize(self.full_name) > self.max_file_size:
            self._roll_files()

        with open(self.full_name, "a+") as f:
            timestamp = datetime.now().isoformat(timespec='milliseconds')
            f.write(f"{timestamp} - {message}\n")

    def _roll_files(self):
        for i in range(self.log_file_count - 1, 0, -1):
            old_name = f"{self.full_name}.{i}"
            new_name = f"{self.full_name}.{i + 1}"
            if os.path.exists(old_name):
                os.rename(old_name, new_name)
                
        # change current one to this name
        if os.path.exists(self.full_name):
            os.rename(self.full_name, f"{self.full_name}.1")