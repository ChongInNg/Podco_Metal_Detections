from serial_server import SerialServer
from log_manager import LogManager
import time
if __name__ == "__main__":
    server = SerialServer(port='COM2', baudrate=115200, timeout=None)
    if not server.connect():
        exit(100)
    # LogManager.instance().start()
    while True:
        time.sleep(1)
    print("This is metal detection server.")