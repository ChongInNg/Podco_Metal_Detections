import asyncio
from serial_server import SerialServer
from log_manager import LogManager
from log.logger import Logger
import time
import os
from websocket.websocket_server import WebSocketServer

def get_current_program_folder():
  return os.path.dirname(os.path.abspath(__file__))

async def start_web_server():
    websocketsrv = WebSocketServer(
        "0.0.0.0", 
        8765
    )
    try:
        await websocketsrv.run()
    except asyncio.CancelledError:
        Logger.info("Web server was cancelled.")
    finally:
        Logger.info("Web server cleanup completed.")

if __name__ == "__main__":
    Logger.info("Podco Metal Detection Server Start")
    if not SerialServer.instance().connect(port='COM2', baudrate=115200, timeout=None):
        Logger.error("Podco Metal Detection Serial Server exited")
        exit(100)

    LogManager.instance().setup(f"{get_current_program_folder()}/system_logs")
    try:
        asyncio.run(start_web_server())
    except KeyboardInterrupt:
        Logger.info("Shutting down web server...")
    finally:
        Logger.info("All Servers shutdown complete.")
    print("This is metal detection server.")