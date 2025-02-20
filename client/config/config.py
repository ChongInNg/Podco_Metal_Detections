import json
import threading

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.file_path = "./config.json"

        self.id: str = ""
        self.slider_range_min: int = 0
        self.slider_range_max: int = 0
        self.slider_step: int = 0
        self.server_address: str = ""
        self.server_port: int = 0
        self.run_on: str = ""
        self.support_keyboard: str = ""
        self.idle_time: int = 0
        self.brightness = 0

    def to_dict(self):
        return {
            "id": self.id,
            "slider_range_min": self.slider_range_min,
            "slider_range_max": self.slider_range_max,
            "slider_step": self.slider_step,
            "server_address": self.server_address,
            "server_port": self.server_port,
            "run_on": self.run_on,
            "support_keyboard": self.support_keyboard,
            "idle_time": self.idle_time,
            "brightness": self.brightness
        }
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
            
            self.id = data.get("id", "")
            self.slider_range_min = data.get("slider_range_min", 0)
            self.slider_range_max = data.get("slider_range_max", 0)
            self.slider_step = data.get("slider_step", 0)
            self.server_address = data.get("server_address", "")
            self.server_port = data.get("server_port", 0)
            self.run_on = data.get("run_on", "")
            self.support_keyboard = data.get("support_keyboard", "")
            self.idle_time = data.get("support_keyboard", 30)
            self.brightness = data.get("brightness", 50)
            self.file_path = file_path

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")

    def run_on_rpi(self) -> bool:
        return self.run_on == "rpi"
    
    def is_support_keyboard(self) -> bool:
        return self.support_keyboard.lower() == "true"

    def save_brightness(self, brightness: int) -> bool:
        try:
            self.brightness = brightness
            with open(self.file_path, "w") as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"save brightness success. value: {brightness}")
            return True
        except Exception as e:
            print(f"save brightness failed. error: {e}")
            return False
# config = Config.instance()
# config.read_config("config.json")
# print(config) 
