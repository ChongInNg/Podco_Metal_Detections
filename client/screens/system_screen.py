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
import sys
import os
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from share.wsmessage import GetFirmwareVersionRequest, GetHardwareVersionRequest, UpdateFirmwareRequest

Builder.load_file("kv/system_screen.kv")

DEFAULT_VERSION:str = "N/A"
class SystemScreen(Screen):
    title = StringProperty('System')
    firmware_version = StringProperty(DEFAULT_VERSION)
    hardware_version = StringProperty(DEFAULT_VERSION)
    current_button = StringProperty('upgrade_btn')
    versions_loaded = BooleanProperty(False)
    show_retry_button = BooleanProperty(False)
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

        self.common_popup = CommonPopup()
        self.progress_popup = ProgressPopup()
        self.confirmation_popup = ConfirmationPopup()

        self.firmware_response_received = False
        self.hardware_response_received = False

        self.response_timeout_event = None
        self.upload_timeout_event = None
    
    def get_button_ids(self):
        if self.show_retry_button:
            return ['retry_btn', 'back_btn']
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
        self.show_retry_button = False
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

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        firmware_versions_dir = os.path.join(base_dir, "firmware_versions")

        if self.hardware_version == DEFAULT_VERSION:
            Logger.debug("Hardware version not available, cannot check firmware files")
            return

        hw_version_dir = os.path.join(firmware_versions_dir, self.hardware_version)
        upgrade_dir = os.path.join(hw_version_dir, "upgrade")
        rollback_dir = os.path.join(hw_version_dir, "rollback")

        if os.path.exists(upgrade_dir):
            upgrade_files = glob.glob(os.path.join(upgrade_dir, "*.img"))
            if upgrade_files:
                self.upgrade_available = True
                upgrade_filename = os.path.basename(upgrade_files[0])
                self.upgrade_version = os.path.splitext(upgrade_filename)[0]
                Logger.debug(f"Upgrade firmware found: {upgrade_files[0]}, version: {self.upgrade_version}")
            else:
                Logger.debug(f"No .img file found in {upgrade_dir}")
        else:
            Logger.debug(f"Upgrade directory not found: {upgrade_dir}")

        if os.path.exists(rollback_dir):
            rollback_files = glob.glob(os.path.join(rollback_dir, "*.img"))
            if rollback_files:
                self.rollback_available = True
                rollback_filename = os.path.basename(rollback_files[0])
                self.rollback_version = os.path.splitext(rollback_filename)[0]
                Logger.debug(f"Rollback firmware found: {rollback_files[0]}, version: {self.rollback_version}")
            else:
                Logger.debug(f"No .img file found in {rollback_dir}")
        else:
            Logger.debug(f"Rollback directory not found: {rollback_dir}")

        Logger.debug(f"Firmware availability - Upgrade: {self.upgrade_available} ({self.upgrade_version}), Rollback: {self.rollback_available} ({self.rollback_version})")

    def request_versions(self):
        if not WebSocketClient.instance().is_connected():
            Logger.warning("WebSocket not connected, cannot request versions")
            return

        self.show_retry_button = False
        self.firmware_response_received = False
        self.hardware_response_received = False
   
        self.loading_screen.update_message("Loading versions...")
        self.loading_screen.show(enable_timeout=True)

        firmware_msg = GetFirmwareVersionRequest.create_message()
        WebSocketClient.instance().send_json_sync(firmware_msg.to_json())
        Logger.debug("Sent GetFirmwareVersionRequest to server")

        hardware_msg = GetHardwareVersionRequest.create_message()
        WebSocketClient.instance().send_json_sync(hardware_msg.to_json())
        Logger.debug("Sent GetHardwareVersionRequest to server")

    def get_firmware_version_ack(self):
        Logger.debug("Received get firmware version ack")
        if self.loading_screen.is_showing():
            self.loading_screen.update_message("Got firmware vesion ack")

    def get_hardware_version_ack(self):
        Logger.debug("Received get hardware version ack")
        if self.loading_screen.is_showing():
            self.loading_screen.update_message("Got hardware vesion ack")

    def update_firmware_version_response(self, major: int, minor:int, bugfix: int):
        self.firmware_response_received = True
        self.firmware_version = f"{major}.{minor}.{bugfix}"
        Logger.debug(f"Firmware version updated: { self.firmware_version}")
        if self.loading_screen.is_showing():
            self.loading_screen.update_message(f"Got firmware vesion: {self.firmware_version}")
        self.check_all_responses_received()

    def update_hardware_version_response(self, major: int, minor:int, bugfix: int):
        self.hardware_response_received = True
        self.hardware_version = f"{major}.{minor}.{bugfix}"
        Logger.debug(f"Hardware version updated: {self.hardware_version}")
        if self.loading_screen.is_showing():
            self.loading_screen.update_message(f"Got hardware vesion: {self.hardware_version}")
        self.check_all_responses_received()

    def check_all_responses_received(self):
        if self.firmware_response_received and self.hardware_response_received:
            Logger.debug("Both version responses received, hiding loading screen")
            self.loading_screen.hide()

            self.versions_loaded = True
            self.show_retry_button = False

            self.check_firmware_availability()

            button_ids = self.get_button_ids()
            self.current_button = button_ids[0]
            self.set_focus_button(self.current_button)

    def on_version_request_timeout(self):
        Logger.warning("Version request timed out")

        if not self.firmware_response_received:
            self.firmware_version = DEFAULT_VERSION
        if not self.hardware_response_received:
            self.hardware_version = DEFAULT_VERSION

        self.versions_loaded = False
        self.show_retry_button = True

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
        all_button_ids = ['upgrade_btn', 'rollback_btn', 'retry_btn', 'back_btn']
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
        elif self.current_button == 'retry_btn':
            self.on_retry_btn_click()
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
        self.progress_popup.update_status("Reseting device to bootloader...")
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
        self.progress_popup.update_status("Reseting device to bootloader...")
        self.progress_popup.handle_open()

        self.response_timeout_event = Clock.schedule_once(self._on_response_timeout, 5.0)

    def on_retry_btn_click(self):
        Logger.debug("Retry button clicked - requesting versions again")
        self.request_versions()

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
            self.progress_popup.update_status("Reset to bootloader success.")
            self.upload_timeout_event = Clock.schedule_once(self._on_update_timeout, 30.0)
        else:
            self.progress_popup.update_status("Reset to bootloader failed!")
            Clock.schedule_once(lambda dt: self._finish_update_with_error(), 2.0)

    def handle_notify_firmware_progress(self, total, progress: int):
        Logger.debug(f"Received notify firmware progress. total: {total}, progress: {progress}")
        if self.progress_popup.is_showing():
            self.progress_popup.update_all("Uploading firmware...", progress, total)

            if progress >= total:
                if self.upload_timeout_event:
                    Clock.unschedule(self.upload_timeout_event)
                    self.upload_timeout_event = None

                self.progress_popup.update_status("Firmware update completed!")
                Clock.schedule_once(lambda dt: self._finish_update(), 2.0)

    def _finish_update(self):
        self._cancel_all_update_timers()

        self.progress_popup.handle_dismiss()
        Logger.debug("Firmware update process finished successfully")

    def _finish_update_with_error(self):
        self._cancel_all_update_timers()

        self.progress_popup.handle_dismiss()
        Logger.debug("Firmware update process finished with error")

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
            self.progress_popup.update_status("Response timeout!")
            Clock.schedule_once(lambda dt: self._finish_update_with_error(), 2.0)

    def _on_update_timeout(self, dt):
        Logger.warning("Firmware update timeout")
        self.upload_timeout_event = None

        if self.progress_popup.is_showing():
            self.progress_popup.update_status("Firmware update timeout!")
            Clock.schedule_once(lambda dt: self._finish_update_with_error(), 2.0)
