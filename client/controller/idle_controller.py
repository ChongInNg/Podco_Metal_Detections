from typing import Callable
from datetime import datetime
import threading
import time
from kivy.clock import Clock
from log.logger import Logger

class IdleController:
    def __init__(self, idle_seconds: int, callback: Callable):
        self.idle_seconds = idle_seconds
        self.timeout_callback = callback
        self.last_clicked_at = None
        self._stop_event = threading.Event()
        self._thread = None
        self._is_skipped = False

    def start(self):
        self.last_clicked_at = datetime.now()
        self._stop_event.clear()
        self._is_skipped = False
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._monitor_idle, daemon=True)
            self._thread.start()

    def checking_timeout(self):
        if self._is_skipped or self.last_clicked_at is None:
            return
        
        current_time = datetime.now()
        elapsed_seconds = (current_time - self.last_clicked_at).total_seconds()
        if elapsed_seconds >= self.idle_seconds:
            Clock.schedule_once(lambda dt: self.timeout_callback())

    def set_skip_checking(self, is_skip: bool):
        self._is_skipped = is_skip

    def update_clicked(self):
        self.last_clicked_at = datetime.now()
        Logger.debug(f"update last click at. {self.last_clicked_at}")

    def _monitor_idle(self):
        while not self._stop_event.is_set():
            self.checking_timeout()
            time.sleep(1) 

    def stop(self):
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

