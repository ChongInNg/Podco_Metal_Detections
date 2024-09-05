import json
import threading
from log.logger import Logger

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.metal_detection_id: str = ""
        self.win_serial_port: str = ""
        self.rpi_serial_port: str = ""
        self.serial_baudrate: int = 0
        self.server_address: str = ""
        self.server_port: int = 0
        self.run_on: str = ""
        self.support_keyboard: str = ""
        self.server_status_pin: int = 0
        self.back_log_count: int = 0

    @classmethod
    def instance(cls) -> "ConfigManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def read_config(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.metal_detection_id = data.get("metal_detection_id", "")
            self.win_serial_port = data.get("win_serial_port", "")
            self.rpi_serial_port = data.get("rpi_serial_port", "")
            self.serial_baudrate = data.get("serial_baudrate", 0)
            self.server_address = data.get("server_address", "")
            self.server_port = data.get("server_port", 0)
            self.run_on = data.get("run_on", "")
            self.support_keyboard = data.get("support_keyboard", "")
            self.server_status_pin = data.get("server_status_pin", 0)
            self.back_log_count = data.get("back_log_count", 10)
            self.back_log_size = data.get("back_log_size", 104857600)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            Logger.error(f"Error loading config: {e}")

    def run_on_rpi(self) -> bool:
        return self.run_on == "rpi"
    
    def is_support_keyboard(self) -> bool:
        return self.support_keyboard.lower() == "true"
# config = Config.instance()
# config.read_config("config.json")
# print(config) 
