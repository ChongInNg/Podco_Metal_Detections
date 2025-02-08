import asyncio
import websockets
import threading
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

class WebSocketClient:
    def __init__(self, url, message_callback=None, disconnect_callback=None):
        self.url = url
        self.message_callback = message_callback
        self.running = False
        self.thread = None
        self.retry_delay = 1
        self.websocket = None
        self.disconnect_callback = disconnect_callback

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
        while self.running:
            try:
                async with websockets.connect(self.url) as websocket:
                    print(f"Connected to WebSocket server: {self.url}")
                    self.websocket = websocket
                    register_req = self.compose_register_request()
                    await websocket.send(register_req.to_json())
                    while self.running:
                        message = await websocket.recv()
                        await self.handle_websocket_messages(message)
                            
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                self.websocket = None
                self.disconnect_callback()
                print(f"Excuted disconnect callback.")
                await asyncio.sleep(self.retry_delay)
            

    def compose_register_request(self) -> RegistrationWsRequest:
        return RegistrationWsRequest.create_message(device_id="detecotr2")
    
    def compose_get_last_n_detections_req(self, last_n: int) ->GetLastNDetectionsRequest:
        return GetLastNDetectionsRequest.create_message(last_n=last_n)
    
    async def handle_websocket_messages(self, message: str):
        try:
            msg_dict = json.loads(message)
            print(f"Decode message success: {msg_dict}\n")
            msg = BaseWsMessage.from_dict(msg_dict)

            # handle the callback in ui first
            if self.message_callback:
                self.message_callback(msg)
            else:
                print(f"cannot handle this message without callback.message: {msg}")

            # handle the response after ui updated
            if isinstance(msg, RegistrationWsResponse):
                await self._handle_registration_response(msg)
        except Exception as ex:
            print(f"handle_websocket_messages failed. error: {ex}\n")

    async def _handle_registration_response(self, resp: RegistrationWsResponse):
        if resp.is_success():
            last_n_detecions_req = self.compose_get_last_n_detections_req(last_n=10)
            await self.websocket.send(last_n_detecions_req.to_json())
