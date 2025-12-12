"""Custom progress notifier for firmware update using pymdfu"""
from pymdfu.mdfu import ProgressNotifier
from log.logger import Logger
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import NotifyFirmwareProgress
from websocket.connection_manager import ConnectionManager

class FirmwareProgressNotifier(ProgressNotifier):
    def __init__(self, total=1000):
        super().__init__(total=total)
        self._current_progress = 0
        Logger.info(f"FirmwareProgressNotifier initialized with total: {total}")

    def update(self, increment):
        self._current_progress += increment

        if self._current_progress > self._total:
            self._current_progress = self._total

        Logger.debug(f"Firmware update progress: {self._current_progress}/{self._total}")

        self._send_progress_update()

    def finalize(self):
        self._current_progress = self._total
        Logger.info(f"Firmware update finalized. Progress: {self._current_progress}/{self._total}")

        self._send_progress_update()

    def close(self):
        Logger.info("FirmwareProgressNotifier closed")

    def update_total(self, new_total):
        self._total = new_total
        Logger.debug(f"Firmware update total updated to: {new_total}")

    def _send_progress_update(self):
        try:
            percentage = (self._current_progress / self._total * 100) if self._total > 0 else 0.0
            percentage = round(percentage, 2)

            message = NotifyFirmwareProgress.create_message(
                total=int(self._total),
                progress=int(self._current_progress),
                percentage=percentage
            )

            connection_manager = ConnectionManager.instance()
            connection_manager.put_message_to_queue(message)

        except Exception as e:
            Logger.error(f"Failed to send firmware progress update: {e}")
