"""Firmware Image Manager - Shared between client and server"""
import os
import glob
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

@dataclass
class FirmwareInfo:
    hardware_version: str
    action: str
    version: str
    file_path: str
    exists: bool

    def to_dict(self):
        return {
            "hardware_version": self.hardware_version,
            "action": self.action,
            "version": self.version,
            "file_path": self.file_path,
            "exists": self.exists
        }


class FirmwareImageManager:
    FIRMWARE_DIR_NAME = "firmware_versions"
    ACTION_UPGRADE = "upgrade"
    ACTION_ROLLBACK = "rollback"
    FIRMWARE_EXTENSION = ".img"

    ACTION_RESET_TO_FACTORY = "reset_to_factory"
    FACTORY_HARDWARE_VERSION = "2.0.0"

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.base_dir = base_dir
        self.firmware_dir = os.path.join(base_dir, self.FIRMWARE_DIR_NAME)

    def get_firmware_dir(self, hardware_version: str, action: str) -> str:
        return os.path.join(self.firmware_dir, hardware_version, action)

    def get_firmware_info(self, firmware_dir: str, hardware_version: str, action: str) -> FirmwareInfo:
        if not os.path.exists(firmware_dir):
            return FirmwareInfo(
                hardware_version=hardware_version,
                action=action,
                version="",
                file_path="",
                exists=False
            )
        img_files = glob.glob(os.path.join(firmware_dir, f"*{self.FIRMWARE_EXTENSION}"))
        if not img_files:
            return FirmwareInfo(
                hardware_version=hardware_version,
                action=action,
                version="",
                file_path="",
                exists=False
            )
        img_file = img_files[0]
        filename = os.path.basename(img_file)
        version = os.path.splitext(filename)[0]
        return FirmwareInfo(
            hardware_version=hardware_version,
            action=action,
            version=version,
            file_path=img_file,
            exists=True
        )

    def get_firmware_path(self, hardware_version: str, action: str) -> Optional[str]:
        firmware_dir = self.get_firmware_dir(hardware_version, action)
        info = self.get_firmware_info(firmware_dir, hardware_version, action)
        return info.file_path if info.exists else None

    def firmware_exists(self, hardware_version: str, action: str) -> bool:
        firmware_dir = self.get_firmware_dir(hardware_version, action)
        info = self.get_firmware_info(firmware_dir, hardware_version, action)
        return info.exists

    def get_firmware_version(self, hardware_version: str, action: str) -> str:
        firmware_dir = self.get_firmware_dir(hardware_version, action)
        info = self.get_firmware_info(firmware_dir, hardware_version, action)
        return info.version

    def get_factory_firmware_path(self) -> Optional[str]:
        firmware_dir = os.path.join(self.firmware_dir, "factory")
        info = self.get_firmware_info(firmware_dir, self.FACTORY_HARDWARE_VERSION, self.ACTION_RESET_TO_FACTORY)
        return info.file_path if info.exists else None
    
    def get_factory_firmware_version(self) -> str:
        firmware_dir = os.path.join(self.firmware_dir, "factory")
        info = self.get_firmware_info(firmware_dir, self.FACTORY_HARDWARE_VERSION, self.ACTION_RESET_TO_FACTORY)
        return info.version if info.exists else "N/A"