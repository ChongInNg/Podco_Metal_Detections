import json
import threading
from dataclasses import dataclass, asdict


@dataclass
class JoyStickPins:
    up: int
    down: int
    left: int
    right: int
    center: int

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class KeypadPins:
    up: int
    down: int
    left: int
    right: int
    center: int

    def to_dict(self) -> dict:
        return asdict(self)

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.file_path = "./config.json"

        self.id: str = ""
        self.logo_tile: str = ""
        self.version: str = ""
        self.slider_range_min: int = 0
        self.slider_range_max: int = 0
        self.slider_step: int = 0
        self.server_address: str = ""
        self.server_port: int = 0
        self.run_on: str = ""
        self.support_keyboard: str = ""
        self.idle_seconds: int = 0
        self.enable_idle_checking: str = ""
        self.brightness = 0
        self.brightness_step = 0
        self.joystick_pins = JoyStickPins(0,0,0,0,0)
        self.keypad_pins = KeypadPins(0,0,0,0,0)
        self.control_mode: str = ""
        self.flip_screen: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "logo_title": self.logo_tile,
            "version": self.version,
            "slider_range_min": self.slider_range_min,
            "slider_range_max": self.slider_range_max,
            "slider_step": self.slider_step,
            "server_address": self.server_address,
            "server_port": self.server_port,
            "run_on": self.run_on,
            "support_keyboard": self.support_keyboard,
            "idle_seconds": self.idle_seconds,
            "enable_idle_checking": self.enable_idle_checking,
            "brightness": self.brightness,
            "brightness_step": self.brightness_step,
            "joystick": self.joystick_pins.to_dict(),
            "keypad": self.keypad_pins.to_dict(),
            "control_mode": self.control_mode,
            "flip_screen": self.flip_screen
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
            self.file_path = file_path

            self.id = data.get("id", "")
            self.logo_tile = data.get("logo_title", "")
            self.version = data.get("version", "")

            self.slider_range_min = data.get("slider_range_min", 0)
            self.slider_range_max = data.get("slider_range_max", 0)
            self.slider_step = data.get("slider_step", 0)
            self.server_address = data.get("server_address", "")
            self.server_port = data.get("server_port", 0)
            self.run_on = data.get("run_on", "")
            if self.run_on != "win" and self.run_on != "rpi":
                raise ValueError("run_on config value is wrong.")
            self.support_keyboard = data.get("support_keyboard", "")
            self.idle_seconds = data.get("idle_seconds", 30)
            self.enable_idle_checking = data.get("enable_idle_checking", "")
            self.brightness = data.get("brightness", 50)
            self.brightness_step = data.get("brightness_step", 1)
            joystick:dict = data.get("joystick")
            if joystick is None or not isinstance(joystick, dict):
                raise ValueError("missing joystick config")
            self.joystick_pins.up = joystick.get("up")
            self.joystick_pins.down = joystick.get("down")
            self.joystick_pins.left = joystick.get("left")
            self.joystick_pins.right = joystick.get("right")
            self.joystick_pins.center = joystick.get("center")

            keypad = data.get("keypad")
            if keypad is None or not isinstance(keypad, dict):
                raise ValueError("missing joystick config")
            self.keypad_pins.up = keypad.get("up")
            self.keypad_pins.down = keypad.get("down")
            self.keypad_pins.left = keypad.get("left")
            self.keypad_pins.right = keypad.get("right")
            self.keypad_pins.center = keypad.get("center")

            self.control_mode = data.get("control_mode", "")
            if self.control_mode != "joystick" and self.control_mode != "keypad":
                raise ValueError("control_mode value is wrong")
            
            self.flip_screen = data.get("flip_screen", "")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            raise e

    def run_on_rpi(self) -> bool:
        return self.run_on == "rpi"
    
    def is_flip_screen(self) -> bool:
        return self.flip_screen.lower() == "true"
    
    def is_support_keyboard(self) -> bool:
        return self.support_keyboard.lower() == "true"

    def is_enable_idle_checking(self) -> bool:
        return self.enable_idle_checking.lower() == "true"
    
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
