from serial_server import SerialServer
from log_manager import LogManager
from log.logger import Logger
import time
if __name__ == "__main__":
    Logger.instance().info("Podco Metal Detection Server Start")
    server = SerialServer(port='COM2', baudrate=115200, timeout=None)
    if not server.connect():
        Logger.instance().error("Podco Metal Detection Server exited")
        exit(100)
    # LogManager.instance().start()
    while True:
        time.sleep(1)
    print("This is metal detection server.")