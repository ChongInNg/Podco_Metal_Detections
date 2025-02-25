import asyncio
from serial_server import SerialServer
from log_manager import LogManager
from log.logger import Logger
import time
import os
import signal
import sys
from websocket.websocket_server import WebSocketServer
from config.config import ConfigManager


def signal_handler(sig, frame):
    sig_name = signal.Signals(sig).name 
    print(f"Received signal: {sig_name} (#{sig})")
    SerialServer.instance().close()
    print("Shutting down server gracefully...")
    sys.exit(1)

signal.signal(signal.SIGTERM, signal_handler)

def get_current_program_folder():
  return os.path.dirname(os.path.abspath(__file__))

async def start_web_server():
    websocketsrv = WebSocketServer(
        ConfigManager.instance().server_address, 
        ConfigManager.instance().server_port
    )
    try:
        await websocketsrv.run()
    except asyncio.CancelledError:
        Logger.info("Web server was cancelled.")
    finally:
        Logger.info("Web server cleanup completed.")

if __name__ == "__main__":
    Logger.info("Podco Metal Detection Server Start")
    port = ''
    config_path = f"{get_current_program_folder()}/config/config.json"
    ConfigManager.instance().read_config(config_path)
    # port = 'ttyAMA0'
    if ConfigManager.instance().run_on_rpi():
        port = ConfigManager.instance().rpi_serial_port
    else:
        port = ConfigManager.instance().win_serial_port
    baudrate = ConfigManager.instance().serial_baudrate

    while not SerialServer.instance().connect(port=port, baudrate=baudrate, timeout=None):
        Logger.error(f"Serial Server cannot connect to {port} with baudrate: {baudrate} now, keep trying...")
        time.sleep(1)

    LogManager.instance().setup(f"{get_current_program_folder()}/system_logs")
    try:
        asyncio.run(start_web_server())
    except KeyboardInterrupt:
        Logger.info("Shutting down web server...")
    finally:
        SerialServer.instance().close()
        Logger.info("All Servers shutdown complete.")
    print(f"This is {ConfigManager.instance().metal_detection_id}.")