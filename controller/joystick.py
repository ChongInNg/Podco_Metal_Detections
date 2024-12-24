import RPi.GPIO as GPIO
import time
import threading
from kivy.clock import Clock

JOYSTICK_PINS = {
    "UP": 5,
    "DOWN": 6,
    "LEFT": 13,
    "RIGHT": 19,
    "CENTER": 26
}

class JoyStick:
    def __init__(self):
        self.joystick_thread = None
        self.running = True

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        for button, pin in JOYSTICK_PINS.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    
    def run(self):
        self.joystick_thread = threading.Thread(target=self.monitor_joystick)
        self.joystick_thread.start()

    def monitor_joystick(self):
        while self.running:
            if GPIO.input(JOYSTICK_PINS["LEFT"]) == GPIO.LOW:
                # Simulate left button press
                Clock.schedule_once(lambda dt: self.change_screen("left"))
                time.sleep(0.3)  # Debounce
            elif GPIO.input(JOYSTICK_PINS["RIGHT"]) == GPIO.LOW:
                # Simulate right button press
                Clock.schedule_once(lambda dt: self.change_screen("right"))
                time.sleep(0.3)  # Debounce