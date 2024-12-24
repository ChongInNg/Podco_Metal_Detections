import RPi.GPIO as GPIO
import time

# Define GPIO pins for each direction
BUTTONS = {
    "UP": 5,
    "DOWN": 6,
    "LEFT": 13,
    "RIGHT": 19,
    "CENTER": 26
}

def setup():
    # Use Broadcom pin numbering
    GPIO.setmode(GPIO.BCM)

    # Set up each button pin as an input with an internal pull-up resistor
    for button, pin in BUTTONS.items():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_buttons():
    while True:
        for button, pin in BUTTONS.items():
            # Button is pressed when the pin reads LOW (because of pull-up resistor)
            if not GPIO.input(pin):
                print(f"{button} pressed")
                time.sleep(0.2)  # Debounce delay

try:
    setup()
    print("Press the navigation buttons (Ctrl+C to exit)")
    read_buttons()

except KeyboardInterrupt:
    print("Exiting program")
finally:
    GPIO.cleanup()
