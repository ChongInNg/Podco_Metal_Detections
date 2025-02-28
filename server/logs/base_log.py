import json
import os
from threading import Lock


class BaseLog:
    def __init__(self, log_directory:str, file_name:str):
        self.log_directory = log_directory
        self.file_name = file_name
        self.full_name = f"{self.log_directory}/{self.file_name}"
        self.file_lock = Lock()

    def _read_json(self):
        with self.file_lock:
            if os.path.exists(self.full_name):
                with open(self.full_name, "r") as f:
                    return json.load(f)
        return None

    def _write_json(self, data: dict):
        with self.file_lock:
            with open(self.full_name, "w") as f:
                json.dump(data, f, indent=4)

   
    def update_file_name(self, file_name: str):
        with self.file_lock:
            self.file_name = file_name
            self.full_name = f"{self.log_directory}/{self.file_name}"