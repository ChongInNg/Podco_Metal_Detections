from asyncio import Queue, get_event_loop
import asyncio
from typing import Callable
from log.logger import Logger
from .connection import Connection

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import *


class NotifyMessageQueue:
    def __init__(self, get_connections_callback: Callable[[str], list[Connection]], loop: asyncio.AbstractEventLoop):
        self.message_queue = Queue()
        self.running = True
        self.get_connections_callback = get_connections_callback
        self.loop = loop

    async def start(self):
        Logger.info("NotifyMessageQueue started.")
        while self.running:
            message = await self.message_queue.get()
            if message is None:  # Shutdown signal
                Logger.info("NotifyMessageQueue stopping.")
                break
            await self.handle_message(message)

    async def stop(self):
        self.running = False
        await self.message_queue.put(None) # notify to shutdown the queue

    async def enqueue_message(self, message: BaseWsNotify):
        await self.message_queue.put(message)

    def enqueue_message_to_loop(self, message: BaseWsNotify):
        asyncio.run_coroutine_threadsafe(self.message_queue.put(message), self.loop)


    async def handle_message(self, message: BaseWsNotify):
        connections = self.get_connections_callback("only_one")
        if len(connections) == 0:
            Logger.warning(f"No connection found for the only one device. Message: {message.to_dict()}")
            return

        Logger.debug(f"Sending message to device: {message.to_json()}")
        for connection in connections:
            await connection.send_notify_message(message)
