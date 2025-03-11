import json
import os
from threading import Lock
from log.logger import Logger

class BaseLog:
    def __init__(self, log_directory:str, file_name:str):
        self.log_directory = log_directory
        self.file_name = file_name
        self.full_name = f"{self.log_directory}/{self.file_name}"
        self.file_lock = Lock()

    def _read_json(self):
        with self.file_lock:
            if os.path.exists(self.full_name):
                try:
                    with open(self.full_name, "r") as f:
                        return json.load(f)
                except Exception as e:
                    Logger.error(f"load json file error. file: {self.full_name}, err: {e}")
        return None

    def _write_json(self, data: dict):
        with self.file_lock:
            with open(self.full_name, "w") as f:
                json.dump(data, f, indent=4)
