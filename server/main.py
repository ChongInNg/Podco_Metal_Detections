from uart_server import UartServer
from log_manager import LogManager
import time
if __name__ == "__main__":
    server = UartServer(port='COM3', baudrate=115200, timeout=None)
    server.connect()
    # LogManager.instance().start()
    while True:
        time.sleep(1)
    print("This is metal detection server.")