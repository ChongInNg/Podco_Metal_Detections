from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from log.logger import Logger
from websocket.client import WebSocketClient
from screens.loading_screen import LoadingScreen
from screens.common_popup import CommonPopup
from screens.progress_popup import ProgressPopup
from screens.confirmation_popup import ConfirmationPopup
from controller.device_detector import DeviceDetector
from config.config import ConfigManager
import sys
import os
import glob
import threading
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import GetFirmwareVersionRequest, UpdateFirmwareRequest, ResetToFactoryFirmwareRequest
from share.firmware_image_manager import FirmwareImageManager

Builder.load_file("kv/system_screen.kv")

DEFAULT_VERSION:str = "N/A"
class SystemScreen(Screen):
    title = StringProperty('System')
    firmware_version = StringProperty(DEFAULT_VERSION)
    hardware_version = StringProperty(DEFAULT_VERSION)
    current_button = StringProperty('upgrade_btn')
    versions_loaded = BooleanProperty(False)
    show_reset_button = BooleanProperty(False)
    upgrade_available = BooleanProperty(False)
    rollback_available = BooleanProperty(False)
    upgrade_version = StringProperty("")
    rollback_version = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_screen = LoadingScreen(
            timeout=10,
            on_timeout_callback=self.on_version_request_timeout
        )
        self.for_debug = False

        self.common_popup = CommonPopup()
        self.progress_popup = ProgressPopup()
        self.confirmation_popup = ConfirmationPopup()

        self.firmware_response_received = False

        self.response_timeout_event = None
        self.upload_timeout_event = None
        
        self.usb_copy_in_progress = False
        self.backup_folder_path = None
        self.copied_from_usb = False
        self.device_detector = DeviceDetector(mount_point=ConfigManager.instance().mount_point)
    
    def get_button_ids(self):
        if self.show_reset_button:
            return ['reset_btn', 'back_btn']
        elif self.versions_loaded:
            if self.upgrade_available and self.rollback_available:
                return ['upgrade_btn', 'rollback_btn', 'back_btn']
            else:
                if self.upgrade_available:
                    return ['upgrade_btn',  'back_btn']
                elif self.rollback_available:
                    return ['rollback_btn', 'back_btn']
                else:
                    return ['back_btn']
        else:
            return ['back_btn']

    def on_kv_post(self, base_widget):
        self.reset_data()

    def reset_data(self):
        if not self.for_debug:
            self.firmware_response_received = False
            self.response_timeout_event = None
            self.upload_timeout_event = None
            self.firmware_version = DEFAULT_VERSION
            self.hardware_version = DEFAULT_VERSION
            self.versions_loaded = False

        self.show_reset_button = False
        button_ids = self.get_button_ids()
        self.current_button = button_ids[0]
        self.set_focus_button(self.current_button)
        if not self.versions_loaded:
            self.request_versions()

    def check_firmware_availability(self):
        self.upgrade_available = False
        self.rollback_available = False
        self.upgrade_version = ""
        self.rollback_version = ""

        if self.hardware_version == DEFAULT_VERSION:
            Logger.debug("Hardware version not available, cannot check firmware files")
            return

        firmware_manager = FirmwareImageManager()

        upgrade_info = firmware_manager.get_firmware_info(self.hardware_version, FirmwareImageManager.ACTION_UPGRADE)
        if upgrade_info and upgrade_info.exists:
            self.upgrade_available = True
            self.upgrade_version = upgrade_info.version
            Logger.debug(f"Upgrade firmware found: {upgrade_info.file_path}, version: {self.upgrade_version}")
        else:
            Logger.debug("No upgrade firmware found")

        rollback_info = firmware_manager.get_firmware_info(self.hardware_version, FirmwareImageManager.ACTION_ROLLBACK)
        if rollback_info and rollback_info.exists:
            self.rollback_available = True
            self.rollback_version = rollback_info.version
            Logger.debug(f"Rollback firmware found: {rollback_info.file_path}, version: {self.rollback_version}")
        else:
            Logger.debug("No rollback firmware found")

        Logger.debug(f"Firmware availability - Upgrade: {self.upgrade_available} ({self.upgrade_version}), Rollback: {self.rollback_available} ({self.rollback_version})")

    def check_usb_firmware_availability(self) -> bool:
        if not ConfigManager.instance().run_on_rpi():
            Logger.debug("Not running on RPi, skipping USB firmware check")
            return False
        
        if self.hardware_version == DEFAULT_VERSION:
            Logger.debug("Hardware version not available, cannot check USB firmware")
            return False

        usb_detected = self.device_detector.detect()
        if not usb_detected:
            Logger.debug("No USB device detected")
            return False
        
        usb_firmware_path = os.path.join(
            ConfigManager.instance().mount_point,
            FirmwareImageManager.FIRMWARE_DIR_NAME,
            self.hardware_version
        )
        
        if os.path.exists(usb_firmware_path):
            Logger.debug(f"USB firmware folder found: {usb_firmware_path}")
            Clock.schedule_once(lambda dt: self.show_usb_firmware_confirmation(), 0.1)
            return True
        else:
            Logger.debug(f"USB firmware folder not found at: {usb_firmware_path}")
            self.device_detector.umount_device()
            return False

    def show_usb_firmware_confirmation(self):
        self.confirmation_popup.reset_state()
        self.confirmation_popup.title = "USB Firmware Detected"
        self.confirmation_popup.update_message(
            f"Firmware found on USB for hardware {self.hardware_version}.\n"
            "Copy firmware from USB?"
        )
        self.confirmation_popup.on_confirm_callback = self._start_usb_firmware_copy
        self.confirmation_popup.handle_open()

    def _start_usb_firmware_copy(self):
        Logger.debug("Starting USB firmware copy process...")

        self.usb_copy_in_progress = True
        self.copied_from_usb = False

        self.loading_screen.update_message("Preparing to copy firmware from USB...")
        self.loading_screen.show(enable_timeout=False)

        copy_thread = threading.Thread(
            target=self._execute_usb_firmware_copy,
            daemon=True
        )
        copy_thread.start()

    def _execute_usb_firmware_copy(self):
        backup_created = False
        copy_successful = False

        try:
            firmware_manager = FirmwareImageManager()
            local_firmware_base = firmware_manager.firmware_dir
            local_hw_folder = os.path.join(local_firmware_base, self.hardware_version)
            backup_folder = f"{local_hw_folder}.bak"
            usb_hw_folder = os.path.join(
                ConfigManager.instance().mount_point,
                FirmwareImageManager.FIRMWARE_DIR_NAME,
                self.hardware_version
            )

            if not os.path.exists(usb_hw_folder):
                raise Exception(f"USB firmware folder not found: {usb_hw_folder}")

            Clock.schedule_once(
                lambda dt: self.loading_screen.update_message("Backing up current firmware..."),
                0
            )

            if os.path.exists(local_hw_folder):
                if os.path.exists(backup_folder):
                    shutil.rmtree(backup_folder)

                os.rename(local_hw_folder, backup_folder)
                self.backup_folder_path = backup_folder
                backup_created = True
                Logger.debug(f"Backed up firmware: {local_hw_folder} -> {backup_folder}")

            Clock.schedule_once(
                lambda dt: self.loading_screen.update_message("Copying firmware from USB..."),
                0
            )

            shutil.copytree(usb_hw_folder, local_hw_folder)
            copy_successful = True
            Logger.debug(f"Copied firmware from USB: {usb_hw_folder} -> {local_hw_folder}")

            self.copied_from_usb = True
            Clock.schedule_once(lambda dt: self._on_usb_copy_success(), 0)
        except Exception as e:
            Logger.error(f"USB firmware copy failed: {e}")
            if backup_created and not copy_successful:
                try:
                    if os.path.exists(local_hw_folder):
                        shutil.rmtree(local_hw_folder)
                    if os.path.exists(backup_folder):
                        os.rename(backup_folder, local_hw_folder)
                        Logger.debug("Restored backup after copy failure")
                except Exception as restore_error:
                    Logger.error(f"Failed to restore backup: {restore_error}")

            Clock.schedule_once(lambda dt: self._on_usb_copy_failure(str(e)), 0)

        finally:
            if self.device_detector:
                self.device_detector.umount_device()

            self.usb_copy_in_progress = False

    def _on_usb_copy_success(self):
        Logger.debug("USB firmware copy successful")

        self.loading_screen.hide()
        self.after_response_received()

    def _on_usb_copy_failure(self, error_message: str):
        Logger.error(f"USB firmware copy failed: {error_message}")

        self.loading_screen.hide()
        self.show_error_popup(f"Failed to copy firmware from USB:\n{error_message}")

        self.copied_from_usb = False
        self.backup_folder_path = None

    def _cleanup_usb_copy_state(self, success: bool):
        if not self.copied_from_usb or not self.backup_folder_path:
            Logger.debug("No USB copy state to clean up")
            return

        try:
            if success:
                if os.path.exists(self.backup_folder_path):
                    shutil.rmtree(self.backup_folder_path)
                    Logger.debug(f"Deleted backup folder after successful upgrade: {self.backup_folder_path}")
            else:
                firmware_manager = FirmwareImageManager()
                local_hw_folder = os.path.join(
                    firmware_manager.firmware_dir,
                    self.hardware_version
                )

                # Delete failed firmware
                if os.path.exists(local_hw_folder):
                    shutil.rmtree(local_hw_folder)

                # Restore backup
                if os.path.exists(self.backup_folder_path):
                    os.rename(self.backup_folder_path, local_hw_folder)
                    Logger.debug(f"Restored backup after failed upgrade: {self.backup_folder_path} -> {local_hw_folder}")

        except Exception as e:
            Logger.error(f"Error cleaning up USB copy state: {e}")
        finally:
            self.copied_from_usb = False
            self.backup_folder_path = None

    def request_versions(self):
        if not WebSocketClient.instance().is_connected():
            Logger.warning("WebSocket not connected, cannot request versions")
            return

        self.show_reset_button = False
        self.firmware_response_received = False
   
        self.loading_screen.update_message("Loading versions...")
        self.loading_screen.show(enable_timeout=True)

        firmware_msg = GetFirmwareVersionRequest.create_message()
        WebSocketClient.instance().send_json_sync(firmware_msg.to_json())
        Logger.debug("Sent GetFirmwareVersionRequest to server")

    def got_firmware_version_ack(self):
        Logger.debug("Received get firmware version ack")
        if self.loading_screen.is_showing():
            self.loading_screen.update_message("Got firmware vesion ack")

    def update_firmware_version_response(self, major: int, minor:int, bugfix: int,
                                    h_major: int, h_minor:int, h_bugfix: int):
        self.firmware_response_received = True
        self.firmware_version = f"{major}.{minor}.{bugfix}"
        self.hardware_version = f"{h_major}.{h_minor}.{h_bugfix}"
        Logger.debug(f"Firmware version updated: { self.firmware_version}, {self.hardware_version}")
        if self.loading_screen.is_showing():
            self.loading_screen.update_message(f"Got vesions: {self.firmware_version}, {self.hardware_version}")
            self.loading_screen.hide()
        
        if self.check_usb_firmware_availability():
            return
        
        # don't exist usb firmware, continue normal flow
        self.after_response_received()

    def after_response_received(self):
        Logger.debug("Both version responses received, hiding loading screen")

        self.versions_loaded = True
        self.show_reset_button = False

        self.check_firmware_availability()
        
        button_ids = self.get_button_ids()
        self.current_button = button_ids[0]
        self.set_focus_button(self.current_button)

    def on_version_request_timeout(self):
        Logger.warning("Version request timed out")

        if not self.firmware_response_received:
            self.firmware_version = DEFAULT_VERSION
            self.hardware_version = DEFAULT_VERSION

        self.versions_loaded = False
        self.show_reset_button = True

        button_ids = self.get_button_ids()
        self.current_button = button_ids[0] #retry button
        self.set_focus_button(self.current_button)

        Clock.schedule_once(lambda dt: self.show_error_popup("Request timed out! Please try again."), 0.1)

    def show_error_popup(self, message):
        self.common_popup.update_title("Error")
        self.common_popup.update_message(message)
        self.common_popup.handle_open()

    def get_title(self):
        return self.title

    def on_up_pressed(self):
        if self.loading_screen.is_showing():
            Logger.debug("loading screen is showing. ignore up pressed.")
            return
        if self.common_popup.is_showing():
            Logger.debug("popup is showing, ignore up pressed")
            return
        if self.progress_popup.is_showing():
            Logger.debug("progress popup is showing, ignore up pressed")
            return
        if self.confirmation_popup.is_showing():
            Logger.debug("confirmation popup is showing, ignore up pressed")
            return

        button_ids = self.get_button_ids()
        current_index = button_ids.index(self.current_button)
        new_index = (current_index - 1) % len(button_ids)
        self.current_button = button_ids[new_index]
        self.set_focus_button(self.current_button)

    def on_down_pressed(self):
        if self.loading_screen.is_showing():
            Logger.debug("loading screen is showing. ignore down pressed.")
            return
        if self.common_popup.is_showing():
            Logger.debug("popup is showing, ignore down pressed")
            return
        if self.progress_popup.is_showing():
            Logger.debug("progress popup is showing, ignore down pressed")
            return
        if self.confirmation_popup.is_showing():
            Logger.debug("confirmation popup is showing, ignore down pressed")
            return

        button_ids = self.get_button_ids()
        current_index = button_ids.index(self.current_button)
        new_index = (current_index + 1) % len(button_ids)
        self.current_button = button_ids[new_index]
        self.set_focus_button(self.current_button)

    def on_left_pressed(self):
        if self.confirmation_popup.is_showing():
            self.confirmation_popup.on_left_pressed()
            return
        Logger.debug("Left pressed (not handled in system screen)")

    def on_right_pressed(self):
        if self.confirmation_popup.is_showing():
            self.confirmation_popup.on_right_pressed()
            return
        Logger.debug("Right pressed (not handled in system screen)")

    def clear_focus(self):
        all_button_ids = ['upgrade_btn', 'rollback_btn', 'reset_btn', 'back_btn']
        for button_id in all_button_ids:
            if button_id in self.ids:
                self.ids[button_id].state = "normal"

    def set_focus_button(self, focused_button_id):
        self.clear_focus()
        if focused_button_id in self.ids:
            self.ids[focused_button_id].state = "down"

    def handle_on_enter(self):
        if self.loading_screen.is_showing():
            Logger.debug("loading scree is showing, ignore enter pressed")
            return

        if self.common_popup.is_showing():
            Logger.debug("pop up is showing, dismiss it when enter pressed")
            self.dismiss_popups()
            return

        if self.progress_popup.is_showing():
            if self.progress_popup.is_in_error_state():
                Logger.debug("progress popup is in error state, dismiss it when enter pressed")
                self.progress_popup.handle_dismiss()
            else:
                Logger.debug("progress popup is showing, ignore enter pressed")
            return

        if self.confirmation_popup.is_showing():
            Logger.debug("confirmation popup is showing, handle enter")
            self.confirmation_popup.handle_on_enter()
            return

        if self.current_button == 'upgrade_btn':
            self.on_upgrade_btn_click()
        elif self.current_button == 'rollback_btn':
            self.on_rollback_btn_click()
        elif self.current_button == 'reset_btn':
            self.on_reset_btn_click()
        elif self.current_button == 'back_btn':
            self.on_back_btn_click()
        
    def on_upgrade_btn_click(self):
        if not WebSocketClient.instance().is_connected():
            Logger.error("WebSocket not connected, cannot upgrade firmware")
            Clock.schedule_once(lambda dt: self.show_error_popup("Server not connected!"), 0.1)
            return

        self.confirmation_popup.reset_state()
        self.confirmation_popup.title = "Confirm Upgrade"
        self.confirmation_popup.message_label.text = f"Are you sure you want to upgrade to {self.upgrade_version}"
        self.confirmation_popup.on_confirm_callback = self._execute_upgrade
        self.confirmation_popup.handle_open()

    def on_rollback_btn_click(self):
        if not WebSocketClient.instance().is_connected():
            Logger.error("WebSocket not connected, cannot rollback firmware")
            Clock.schedule_once(lambda dt: self.show_error_popup("Server not connected!"), 0.1)
            return

        self.confirmation_popup.reset_state()
        self.confirmation_popup.title = "Confirm Rollback"
        self.confirmation_popup.message_label.text = f"Are you sure you want to rollback to {self.rollback_version}?"
        self.confirmation_popup.on_confirm_callback = self._execute_rollback
        self.confirmation_popup.handle_open()

    def _execute_upgrade(self):
        Logger.debug("Executing firmware upgrade...")

        update_firmware_msg = UpdateFirmwareRequest.create_message(
            hardware_version=self.hardware_version,
            action="upgrade"
        )
        WebSocketClient.instance().send_json_sync(update_firmware_msg.to_json())
        Logger.debug("Sent UpdateFirmwareRequest (upgrade) to server")

        self.progress_popup.reset()
        self.progress_popup.set_title("Upgrading")
        self.progress_popup.update_status("Reseting device to bootloader")
        self.progress_popup.handle_open()

        self.response_timeout_event = Clock.schedule_once(self._on_response_timeout, 5.0)

    def _execute_rollback(self):
        Logger.debug("Executing firmware rollback...")

        update_firmware_msg = UpdateFirmwareRequest.create_message(
            hardware_version=self.hardware_version,
            action="rollback"
        )
        WebSocketClient.instance().send_json_sync(update_firmware_msg.to_json())
        Logger.debug("Sent UpdateFirmwareRequest (rollback) to server")

        self.progress_popup.reset()
        self.progress_popup.set_title("Rolling Back")
        self.progress_popup.update_status("Reseting device to bootloader")
        self.progress_popup.handle_open()

        self.response_timeout_event = Clock.schedule_once(self._on_response_timeout, 5.0)

    def on_reset_btn_click(self):
        Logger.debug("Reset button clicked - requesting versions again")
        self.confirmation_popup.reset_state()
        self.confirmation_popup.title = "Reset Firmware"
        self.confirmation_popup.message_label.text = f"Are you sure you want to reset to factory firmware?"
        self.confirmation_popup.on_confirm_callback = self._excute_reset
        self.confirmation_popup.handle_open()

    def on_back_btn_click(self):
        Logger.debug("Back button clicked")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_option_screen()

    def show_popups(self):
        if self.common_popup.is_showing():
            self.common_popup.opacity = 1

    def dismiss_popups(self):
        if self.common_popup.is_showing():
            self.common_popup.opacity = 1
            self.common_popup.handle_dismiss(self)

    def handle_update_firmware_response(self, code, message: str):
        Logger.debug(f"Received update firmware response. code: {code}, message: {message}")

        if self.response_timeout_event:
            Clock.unschedule(self.response_timeout_event)
            self.response_timeout_event = None

        if code == "OK":
            self.progress_popup.update_status("Reset to bootloader success")
            self.upload_timeout_event = Clock.schedule_once(self._on_update_timeout, 30.0)
        else:
            self._finish_update_with_error("Reset to bootloader failed!")

    def handle_notify_firmware_progress(self, total, progress: int):
        Logger.debug(f"Received notify firmware progress. total: {total}, progress: {progress}")
        if self.progress_popup.is_showing():
            self.progress_popup.update_all("Uploading firmware...", progress, total)

            if progress >= total:
                if self.upload_timeout_event:
                    Clock.unschedule(self.upload_timeout_event)
                    self.upload_timeout_event = None

    def handle_notify_firmware_result(self, code: str, message: str):
        Logger.debug(f"Received update firmware result. code: {code}, message: {message}")
        if code == "OK":
            if self.current_button == 'upgrade_btn':
                self.firmware_version = self.upgrade_version
            elif self.current_button == 'rollback_btn':
                self.firmware_version = self.rollback_version
            self.progress_popup.update_status("Firmware update completed successfully.")
            Clock.schedule_once(lambda dt: self._finish_update(), 2.0)
        else:
            self._finish_update_with_error("Firmware update failed!")

        self._cleanup_usb_copy_state(success=(code == "OK"))

    def _finish_update(self):
        self._cancel_all_update_timers()

        self.progress_popup.handle_dismiss()
        Logger.debug("Firmware update process finished successfully")

    def _finish_update_with_error(self, error_message: str):
        self._cancel_all_update_timers()

        if self.progress_popup.is_showing():
            self.progress_popup.show_error_state(error_message)
        Logger.debug(f"Firmware update process finished with error: {error_message}")

    def _cancel_all_update_timers(self):
        if self.response_timeout_event:
            Clock.unschedule(self.response_timeout_event)
            self.response_timeout_event = None
        if self.upload_timeout_event:
            Clock.unschedule(self.upload_timeout_event)
            self.upload_timeout_event = None

    def _on_response_timeout(self, dt):
        Logger.warning("Firmware update response timeout")
        self.response_timeout_event = None

        if self.progress_popup.is_showing():
            self._finish_update_with_error("Reset bootloader timeout!")

    def _on_update_timeout(self, dt):
        Logger.warning("Firmware update timeout")
        self.upload_timeout_event = None

        if self.progress_popup.is_showing():
            self._finish_update_with_error("Firmware update timeout!")

    def _excute_reset(self):
        self.progress_popup.reset()
        self.progress_popup.set_title("Resetting")
        self.progress_popup.update_status("Resetting to factory firmware...")
        self.progress_popup.handle_open()

        reset_msg = ResetToFactoryFirmwareRequest.create_message()
        WebSocketClient.instance().send_json_sync(reset_msg.to_json())
        Logger.debug("Sent ResetToFactoryFirmwareRequest to server")

    def handle_reset_to_factory_firmware_response(self, code: str, message: str):
        Logger.debug(f"Received reset to factory firmware response. code: {code}, message: {message}")

        if code == "OK":
            Logger.debug("Reset to factory firmware successful")
            self.progress_popup.update_status("Reseting device to bootloader")
            self.response_timeout_event = Clock.schedule_once(self._on_response_timeout, 5.0)
        elif code == "BootloaderOpened":
            Logger.debug("Bootloader opened after factory reset")
            self.upload_timeout_event = Clock.schedule_once(self._on_update_timeout, 30.0)
        else:
            Logger.debug("Reset to factory firmware failed")
            Clock.schedule_once(lambda dt: self.show_error_popup("Reset to factory firmware failed!"), 0)
