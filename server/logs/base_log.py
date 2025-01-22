import json
import os
from threading import Lock


class BaseLog:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_lock = Lock()

    def _rotate_file(self, index):
        return f"{self.file_prefix}_{index}.json"

    def _read_json(self):
        with self.file_lock:
            if os.path.exists(self.file_name):
                with open(self.file_name, "r") as f:
                    return json.load(f)
        return {}

    def _write_json(self, data: dict):
        with self.file_lock:
            with open(self.file_name, "w") as f:
                json.dump(data, f, indent=4)

    def _check_and_rotate_file(self, index):
        file_path = self._rotate_file(index)
        if os.path.exists(file_path) and os.path.getsize(file_path) > self.max_file_size:
            return index + 1
        return index
