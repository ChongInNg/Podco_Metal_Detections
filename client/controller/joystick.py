import RPi.GPIO as GPIO
import time
import threading
from typing import Callable
from log.logger import Logger
from config.config import ConfigManager
class JoyStick:
    def __init__(self, callback: Callable[[str], None]):
        self.joystick_thread = None
        self.running = True
        self.callback = callback
        self.JOYSTICK_PINS: dict = {
            "UP": 5,
            "DOWN": 6,
            "LEFT": 13,
            "RIGHT": 19,
            "CENTER": 26
        }

        self.previous_states = {
            "UP": GPIO.HIGH,
            "DOWN": GPIO.HIGH,
            "LEFT": GPIO.HIGH,
            "RIGHT": GPIO.HIGH,
            "CENTER": GPIO.HIGH
        }

        self.keep_pressing_seconds = ConfigManager.instance().keep_pressing_seconds

    def setup(self, up: int, down: int, left: int, right: int, center: int):
        self.JOYSTICK_PINS["UP"] = up
        self.JOYSTICK_PINS["DOWN"] = down
        self.JOYSTICK_PINS["LEFT"] = left
        self.JOYSTICK_PINS["RIGHT"] = right
        self.JOYSTICK_PINS["CENTER"] = center
        GPIO.setmode(GPIO.BCM)
        for button, pin in self.JOYSTICK_PINS.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def stop(self):
        self.running = False
        if self.joystick_thread is not None:
            self.joystick_thread.join()
        GPIO.cleanup() 
        Logger.info("JoyStick stopped.")

    def run(self):
        self.joystick_thread = threading.Thread(target=self.monitor_joystick)
        self.joystick_thread.start()

    def check_press_left_right(self):
        if (GPIO.input(self.JOYSTICK_PINS["LEFT"]) == GPIO.LOW and 
            GPIO.input(self.JOYSTICK_PINS["RIGHT"]) == GPIO.LOW):
            start_time = time.time()
            while (GPIO.input(self.JOYSTICK_PINS["LEFT"]) == GPIO.LOW and 
                   GPIO.input(self.JOYSTICK_PINS["RIGHT"]) == GPIO.LOW):
                if time.time() - start_time >= self.keep_pressing_seconds:
                    return True
                time.sleep(0.01)
            return False
        return False

    def check_press_up_down(self):
        if (GPIO.input(self.JOYSTICK_PINS["UP"]) == GPIO.LOW and 
            GPIO.input(self.JOYSTICK_PINS["DOWN"]) == GPIO.LOW):
            start_time = time.time()
            while (GPIO.input(self.JOYSTICK_PINS["UP"]) == GPIO.LOW and 
                   GPIO.input(self.JOYSTICK_PINS["DOWN"]) == GPIO.LOW):
                if time.time() - start_time >= self.keep_pressing_seconds:
                    return True
                time.sleep(0.01)
            return False
        return False
    
    def monitor_joystick(self):
        Logger.debug("monitor_joystick running..........")
        while self.running:
            if self.check_press_left_right():
                Logger.debug(f"Press left right in the same time over {self.keep_pressing_seconds} seconds.")
                self.callback("left_right")
                time.sleep(0.3)
                continue

            if self.check_press_up_down():
                Logger.debug(f"Press up down in the same time over {self.keep_pressing_seconds} seconds.")
                self.callback("up_down")
                time.sleep(0.3)
                continue

            for button_name, pin in self.JOYSTICK_PINS.items():
                current_state = GPIO.input(pin)
                previous_state = self.previous_states[button_name]

                if previous_state == GPIO.HIGH and current_state == GPIO.LOW:
                    direction = button_name.lower()
                    Logger.debug(f"Button pressed: {direction}")
                    self.callback(direction)
                    self.previous_states[button_name] = current_state
                    time.sleep(0.15)
                    break

                elif previous_state == GPIO.LOW and current_state == GPIO.HIGH:
                    direction = button_name.lower() + "_release"
                    Logger.debug(f"Button released: {direction}")
                    self.callback(direction)
                    self.previous_states[button_name] = current_state
                    time.sleep(0.15)
                    break

            time.sleep(0.01)

