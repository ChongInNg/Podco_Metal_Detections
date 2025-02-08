import threading
from typing import Optional
from .connection import Connection
from log.logger import Logger
from .notify_message_queue import NotifyMessageQueue

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *


class ConnectionManager:
    _instance: Optional['ConnectionManager'] = None

    def __init__(self):
        if ConnectionManager._instance is not None:
            raise RuntimeError("ConnectionManager is a singleton. Use ConnectionManager.instance() instead.")
        
        self._lock = threading.Lock()
        self._connections: dict[int, Connection] = {}
        self.notify_queue = None

    def set_notify_queue(self, notify_queue: NotifyMessageQueue):
        self.notify_queue = notify_queue
    @classmethod
    def instance(cls) -> 'ConnectionManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_or_create_connection(self, client_id: int, websocket: any) -> Connection:
        with self._lock:
            connection = self._connections.get(client_id)
            if connection is None:
                Logger.debug(f"Creating a new connection for client: {client_id}")
                connection = Connection(websocket)
                self._connections[client_id] = connection
            return connection
        
    def send_notify_message(self, notify_message: BaseWsNotify):
        try:
            self.notify_queue.enqueue_message_to_loop(notify_message)
        except Exception as e:
            Logger.error(f"Send notify message error: {e}.")
        

    def get_connections(self, device_identity: str) -> list[Connection]:
        connetions:list[Connection] = []
        with self._lock:
            if device_identity == "only_one":
                if len(self._connections) > 0 :
                    frist_conn = next(iter(self._connections.values()))
                    connetions.append(frist_conn)
            else:
                for client_id, connection in self._connections.items():
                    if connection.get_identity() == device_identity:
                        connetions.append(connection)
        return connetions
    
    def delete_connection(self, client_id:int):
        with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]
                print(f"delete connection: {client_id}, current connection len: {len(self._connections)}")
            else:
                print(f"Key: {client_id} not found in connections")
            