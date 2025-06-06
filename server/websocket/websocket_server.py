import asyncio
import websockets
import json
import logging
from log.logger import Logger
from .connection_manager import ConnectionManager 
from .ws_message_queue import WsMessageQueue
from server.serial_server import SerialServer

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *

class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def on_connect(self, websocket):
        client_id = id(websocket)
        Logger.info(f"Client: {client_id} connected to server, remote_addr: {websocket.remote_address}")

        try:
            async for message in websocket:
                data = json.loads(message)
                await self._handle_message(client_id, websocket, data)
        except websockets.exceptions.ConnectionClosedError as ex:
            Logger.error(f"Client: {client_id} was closed", str(ex))
        finally:
            self._handle_disconnect(client_id)
    
    async def run(self):
        try:
            Logger.debug(f"Starting web server, host: {self.host}, {self.port}")
            logging.getLogger("websockets").setLevel(logging.INFO)
            loop = asyncio.get_event_loop()
            connection_manager = ConnectionManager.instance()
            ws_queue = WsMessageQueue(get_connections_callback=connection_manager.get_connections, loop=loop)
            connection_manager.set_ws_queue(ws_queue)
            asyncio.create_task(connection_manager.ws_queue.start())


            async with websockets.serve(self.on_connect, self.host, self.port):
                SerialServer.instance().set_server_status_on()
                await asyncio.Future()
            Logger.debug(f"Web server started....")
        except KeyboardInterrupt:
            Logger.error("Receive KeyboardInterrupt, stop the web server")

    async def _handle_message(self, client_id: int, websocket: any, data: dict) -> None:             
        try:
            message = BaseWsMessage.from_dict(data)
            connection_manager = ConnectionManager.instance()
            connection = connection_manager.get_or_create_connection(client_id, websocket)
            await connection.handle_message(message)
        except ValueError as ve:
            error_rsp = SystemErrorResponse.create_message(f"Invalid message: {ve}")
            await websocket.send(error_rsp.to_json())
        except Exception as e:
            import traceback
            traceback.print_stack()
            Logger.error(f"Error handling message from client {client_id}: {e}")
            error_rsp = SystemErrorResponse.create_message(f"Internal server error: {e}")
            await websocket.send(error_rsp.to_json())

    def _handle_disconnect(self, client_id):
        ConnectionManager.instance().delete_connection(client_id)
        Logger.debug(f"Client: {id} disconnected.")


# if __name__ == "__main__":
#     server = WebSocketServer("0.0.0.0", 8765)
#     asyncio.run(server.run())