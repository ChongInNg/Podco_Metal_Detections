from typing import Optional
from log.logger import Logger
from .client import FirmwareUpdateClient
import threading
import os

class FirmwareUpdateTask:
    def __init__(self, hardware_version: str, action: str, firmware_image_path: str, request_id: str):
        self.hardware_version = hardware_version
        self.action = action
        self.request_id = request_id
        self.firmware_image_path = firmware_image_path

    def to_dict(self):
        return {
            "hardware_version": self.hardware_version,
            "action": self.action,
            "request_id": self.request_id,
            "firmware_image_path": self.firmware_image_path
        }


class FirmwareUpdateManager:  
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if FirmwareUpdateManager._instance is not None:
            raise RuntimeError("FirmwareUpdateManager is a singleton. Use instance() instead.")

        self._pending_task = None
        self._is_updating = False
        self._update_thread = None
        self._port = None
        self._baudrate = None
        Logger.info("FirmwareUpdateManager initialized")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def init_serial_info(self, port: str, baudrate:int):
        self._port = port
        self._baudrate = baudrate

    def set_update_task(self, hardware_version: str, action: str, request_id: str) -> bool:
        with self._lock:
            if self._is_updating:
                Logger.error("Firmware update already in progress. Cannot set new task.")
                return False

            if self._pending_task is not None:
                Logger.warning("Pending firmware update task already exists. Overwriting...")

            self._pending_task = FirmwareUpdateTask(
                hardware_version=hardware_version,
                action=action,
                request_id=request_id
            )

            Logger.info(f"Firmware update task set: {self._pending_task.to_dict()}")
            return True

    def has_pending_task(self) -> bool:
        with self._lock:
            return self._pending_task is not None

    def trigger_update(self) -> bool:
        with self._lock:
            if self._pending_task is None:
                Logger.error("No pending firmware update task to trigger.")
                return False

            if self._is_updating:
                Logger.error("Firmware update already in progress.")
                return False

            self._is_updating = True
            task = self._pending_task

            Logger.info(f"Triggering firmware update for task: {task.to_dict()}")

        self._update_thread = threading.Thread(
            target=self._execute_update,
            args=(task,),
            daemon=True
        )
        self._update_thread.start()

        return True

    def _execute_update(self, task: FirmwareUpdateTask):
        try:
            Logger.info(f"Starting firmware update execution: {task.to_dict()}")

            client = FirmwareUpdateClient(
                port=self._port,
                baudrate=self._baudrate
            )

            success = client.update_firmware(
                firmware_image_path=task.firmware_image_path
            )

            if success:
                Logger.info(f"Firmware update completed successfully for task: {task.request_id}")
                self._send_completion_notification(task, success=True, message="Firmware update completed successfully")
            else:
                Logger.error(f"Firmware update failed for task: {task.request_id}")
                self._send_completion_notification(task, success=False, message="Firmware update failed")

        except Exception as e:
            Logger.error(f"Firmware update execution error: {e}")
            self._send_completion_notification(task, success=False, message=f"Firmware update error: {e}")

        finally:
            with self._lock:
                self._pending_task = None
                self._is_updating = False
                self._update_thread = None

            Logger.info("Firmware update execution completed and cleaned up")

    def _send_completion_notification(self, task: FirmwareUpdateTask, success: bool, message: str):
        try:
            import sys
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
            from share.wsmessage import NotifyFirmwareUpdateResult
            from websocket.connection_manager import ConnectionManager

            msg = NotifyFirmwareUpdateResult.create_message(
                id=task.request_id,
                result="OK" if success else "error",
                message=message,
            )

            connection_manager = ConnectionManager.instance()
            connection_manager.put_message_to_queue(msg)

            Logger.info(f"Firmware update completion notification sent: {msg.to_dict()}")

        except Exception as e:
            Logger.error(f"Failed to send firmware update completion notification: {e}")

    def is_updating(self) -> bool:
        with self._lock:
            return self._is_updating
