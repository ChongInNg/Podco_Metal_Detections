import RPi.GPIO as GPIO
import time
import threading
from typing import Callable
from kivy.clock import Clock

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
        print("Stopping application...")
        self.running = False
        if self.joystick_thread is not None:
            self.joystick_thread.join()
        GPIO.cleanup() 
        print("Application stopped cleanly.")

    def run(self):
        self.joystick_thread = threading.Thread(target=self.monitor_joystick)
        self.joystick_thread.start()

    def monitor_joystick(self):
        print("monitor_joystick running..........")
        while self.running:
            if GPIO.input(self.JOYSTICK_PINS["LEFT"]) == GPIO.LOW:
                Clock.schedule_once(lambda dt: self.callback("left"))
                time.sleep(0.3)
            elif GPIO.input(self.JOYSTICK_PINS["RIGHT"]) == GPIO.LOW:
                Clock.schedule_once(lambda dt: self.callback("right"))
                time.sleep(0.3)
            elif GPIO.input(self.JOYSTICK_PINS["UP"]) == GPIO.LOW:
                Clock.schedule_once(lambda dt: self.callback("up"))
                time.sleep(0.3)
            elif GPIO.input(self.JOYSTICK_PINS["DOWN"]) == GPIO.LOW:
                Clock.schedule_once(lambda dt: self.callback("down"))
                time.sleep(0.3)
            elif GPIO.input(self.JOYSTICK_PINS["CENTER"]) == GPIO.LOW:
                Clock.schedule_once(lambda dt: self.callback("center"))
                time.sleep(0.3)