import asyncio
import websockets
import threading
import os
import sys
from typing import Optional
from log.logger import Logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

class WebSocketClient:
    _instance: Optional['WebSocketClient'] = None

    def __init__(self):
        if WebSocketClient._instance is not None:
            raise RuntimeError("WebSocketClient is a singleton. Use WebSocketClient.instance() instead.")
        self.url = None
        self.message_callback = None
        self.event_loop = None
        self.running = False
        self.thread = None
        self.retry_delay = 1
        self.websocket = None
        self.disconnect_callback = None

    @classmethod
    def instance(cls) -> 'WebSocketClient':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start(self, url, event_loop, message_callback=None, disconnect_callback=None):
        self.url = url
        self.message_callback = message_callback
        self.running = False
        self.thread = None
        self.retry_delay = 1
        self.websocket = None
        self.disconnect_callback = disconnect_callback
        self.event_loop = event_loop
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
 
    def _run(self):
        asyncio.run(self._connect())

    async def _connect(self):
        while self.running:
            try:
                async with websockets.connect(self.url) as websocket:
                    Logger.info(f"Connected to WebSocket server: {self.url}")
                    self.websocket = websocket
                    register_req = RegistrationWsRequest.create_message(device_id="detecotr2")
                    await websocket.send(register_req.to_json())
                    while self.running:
                        message = await websocket.recv()
                        await self.handle_websocket_messages(message)
                            
            except Exception as e:
                Logger.error(f"WebSocket connection error: {e}")
                self.websocket = None
                self.disconnect_callback()
                Logger.info(f"Excuted disconnect callback.")
                await asyncio.sleep(self.retry_delay)
    
    async def handle_websocket_messages(self, message: str):
        try:
            msg_dict = json.loads(message)
            Logger.info(f"Decode ws message success: {msg_dict}")
            msg = BaseWsMessage.from_dict(msg_dict)

            # handle the callback in ui first
            if self.message_callback:
                self.message_callback(msg)
            else:
                Logger.warning(f"cannot handle this message without callback.message: {msg}")

            # handle the response after ui updated
            if isinstance(msg, RegistrationWsResponse):
                await self._handle_registration_response(msg)
        except Exception as ex:
            Logger.error(f"handle_websocket_messages failed. source message: {message}, error: {ex}")

    async def _handle_registration_response(self, resp: RegistrationWsResponse):
        if resp.is_success():
            last_n_detecions_req = GetLastNDetectionsRequest.create_message(last_n=10)
            await self.websocket.send(last_n_detecions_req.to_json())

            get_calibration_req = GetCalibrationRequest.create_message()
            await self.websocket.send(get_calibration_req.to_json())

    def send_json_sync(self, jsonstr: str):
        if len(jsonstr) == 0:
            raise ValueError("cannot send a empty string to server.")
        
        if not self.event_loop.is_running():
            raise RuntimeError("Event loop is not running. Cannot send message.")

        future = asyncio.run_coroutine_threadsafe(
            self.websocket.send(jsonstr),
            self.event_loop
        )
        
        try:
            future.result(timeout=2)
            Logger.info(f"send json success: {jsonstr}")
        except Exception as e:
            Logger.error(f"Failed to send message: {e}")

    def is_connected(self) -> bool:
        return self.websocket != None
            
