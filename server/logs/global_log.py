from datetime import datetime
from .base_log import BaseLog


class GlobalLogData:
    def __init__(self, first_connection, total_run_minutes, last_updated_at, reset_number, reset_at, log_index, max_file_size):
        self.first_connection = datetime.fromisoformat(first_connection)
        self.total_run_minutes = total_run_minutes
        self.last_updated_at = datetime.fromisoformat(last_updated_at)
        self.reset_number = reset_number
        self.reset_at = datetime.fromisoformat(reset_at) if reset_at else None
        self.log_index = log_index
        self.max_file_size = max_file_size

    def to_dict(self):
        return {
            "first_connection": self.first_connection.isoformat(),
            "total_run_minutes": self.total_run_minutes,
            "last_updated_at": self.last_updated_at.isoformat(),
            "reset_number": self.reset_number,
            "reset_at": self.reset_at.isoformat() if self.reset_at else None,
            "log_index": self.log_index,
            "max_file_size": self.max_file_size,
        }
    
class GlobalLog(BaseLog):
    def __init__(self, file_name="global_log.json"):
        super().__init__(file_name=file_name)
        self._init_data()

    def update_global_log(self):
        global_log = self._read_json()
        first_connection = datetime.fromisoformat(global_log["first_connection"])
        total_runtime = (datetime.now() - first_connection).total_seconds() // 60
        global_log["total_run_minutes"] = int(total_runtime)
        global_log["last_updated_at"] = datetime.now().isoformat()

        self._write_json(global_log)

    def _init_data(self):
        global_log = self._read_json()
        if not global_log:
            global_log = {
                "first_connection": datetime.now().isoformat(),
                "total_run_minutes": 0,
                "last_updated_at": datetime.now().isoformat(),
                "reset_number": 0,
                "reset_at": None,
                "log_index": 0,
                "max_file_size": 100 * 1024 * 1024
            }
            self._write_json(global_log)

    def increment_log_index(self, index: int):
        global_log = self._read_json()
        global_log["log_index"] = index
        self._write_json(self.file_name, global_log)

    def get_global_log(self) -> GlobalLogData:
        data = self._read_json()
        return GlobalLogData(
            first_connection = data["first_connection"],
            total_run_minutes = data["total_run_minutes"],
            last_updated_at = data["last_updated_at"],
            reset_number = data["reset_number"],
            reset_at = data["reset_at"],
            log_index = data["log_index"],
            max_file_size = data["max_file_size"],
        )
