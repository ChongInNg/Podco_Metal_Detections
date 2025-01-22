from uart_server import UartServer
from log_manager import LogManager

if __name__ == "__main__":
    # server = UartServer(port='/COM24', baudrate=115200, timeout=None)
    # server.connect()
    LogManager.instance().start()
    print("This is metal detection server.")