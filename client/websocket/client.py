import asyncio
import websockets
import threading
import json
from .message import *

class WebSocketClient:
    def __init__(self, url, message_callback=None):
        self.url = url
        self.message_callback = message_callback
        self.running = False
        self.thread = None

    def start(self):
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
        try:
            async with websockets.connect(self.url) as websocket:
                print(f"Connected to WebSocket server: {self.url}")
                await websocket.send(self.compose_register_message())
                while self.running:
                    message = await websocket.recv()
                    if self.message_callback:
                        self.message_callback(message)
                        
        except Exception as e:
            print(f"WebSocket connection error: {e}")

    def compose_register_message(self) -> str:
        return RegistrationWsRequest.create_message(device_id="detecotr2").to_json()