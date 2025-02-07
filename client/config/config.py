import json
import threading

class Config:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.metal_detection_id: str = ""
        self.analyze_range_min: int = 0
        self.analyze_range_max: int = 0
        self.serial_port: str = ""
        self.websocket_port: int = 0

    @classmethod
    def instance(cls) -> "Config":
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
            self.analyze_range_min = data.get("analyze_range_min", 0)
            self.analyze_range_max = data.get("analyze_range_max", 0)
            self.serial_port = data.get("serial_port", "")
            self.websocket_port = data.get("websocket_port", 0)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")


# config = Config.instance()
# config.read_config("config.json")
# print(config) 
