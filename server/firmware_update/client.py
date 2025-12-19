"""Firmware update client using pymdfu library"""
from pymdfu.mdfu import Mdfu, MdfuUpdateError
from pymdfu.transport.uart_transport import UartTransport
from pymdfu.mac.serial_mac import MacSerialPort
from .progress_notifier import FirmwareProgressNotifier
from log.logger import Logger
from typing import Optional
import os

class FirmwareUpdateClient:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.mdfu_host: Optional[Mdfu] = None
        Logger.info(f"FirmwareUpdateClient initialized with port: {port}, baudrate: {baudrate}")

    def update_firmware(self, firmware_image_path: str) -> bool:
        try:
            if not os.path.exists(firmware_image_path):
                raise FileNotFoundError(f"Firmware image file not found: {firmware_image_path}")

            Logger.info(f"Reading firmware image from: {firmware_image_path}")
            with open(firmware_image_path, 'rb') as f:
                firmware_image = f.read()

            Logger.info(f"Firmware image size: {len(firmware_image)} bytes")

            mac = MacSerialPort(
                port=self.port,
                baudrate=self.baudrate,
            )

            transport = UartTransport(mac=mac, timeout=5)

            self.mdfu_host = Mdfu(transport=transport, retries=5)

            notifier = FirmwareProgressNotifier(total=1000)

            Logger.info("Starting firmware upgrade...")
            self.mdfu_host.run_upgrade(firmware_image, notifier=notifier)

            Logger.info("Firmware upgrade completed successfully!")
            return True

        except FileNotFoundError as e:
            Logger.error(f"Firmware image file error: {e}")
            raise

        except MdfuUpdateError as e:
            Logger.error(f"Firmware update failed: {e}")
            return False

        except Exception as e:
            Logger.error(f"Unexpected error during firmware update: {e}")
            return False

        finally:
            if self.mdfu_host:
                self.mdfu_host.close() 
                self.mdfu_host = None

    def is_bootloader_opened(self) -> bool:
        try:
            mac = MacSerialPort(
                port=self.port,
                baudrate=self.baudrate,
            )

            transport = UartTransport(mac=mac, timeout=1)
            mdfu_host = Mdfu(transport=transport, retries=0)
            mdfu_host.open()
            client_info = mdfu_host.get_client_info()

            Logger.info(f"Bootloader is accessible. Client info: {client_info}")
            return True

        except Exception as e:
            Logger.warning(f"Bootloader not accessible: {e}")
            return False
        finally:
            if mdfu_host:
                mdfu_host.close()

    @staticmethod
    def create_client(port: str, baudrate: int = 115200, timeout: float = 1.0) -> 'FirmwareUpdateClient':
        return FirmwareUpdateClient(port=port, baudrate=baudrate, timeout=timeout)
