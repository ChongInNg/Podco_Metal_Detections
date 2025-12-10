from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from log.logger import Logger

Builder.load_file("kv/system_screen.kv")

class SystemScreen(Screen):
    title = StringProperty('System')
    firmware_version = StringProperty("-.-.-")
    hardware_version = StringProperty("-.-.-")
    current_button = StringProperty('upgrade_btn')
    
    button_ids = ['upgrade_btn', 'rollback_btn', 'back_btn']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_upgrading = False
    
    def on_kv_post(self, base_widget):
        self.reset_data()

    def reset_data(self):
        self.current_button = 'upgrade_btn'
        self.set_focus_button(self.current_button)

    def get_title(self):
        return self.title

    def on_up_pressed(self):
        current_index = self.button_ids.index(self.current_button)
        new_index = (current_index - 1) % len(self.button_ids)
        self.current_button = self.button_ids[new_index]
        self.set_focus_button(self.current_button)
    
    def on_down_pressed(self):
        current_index = self.button_ids.index(self.current_button)
        new_index = (current_index + 1) % len(self.button_ids)
        self.current_button = self.button_ids[new_index]
        self.set_focus_button(self.current_button)
    

    def clear_focus(self):
        for button_id in self.button_ids:
            if button_id in self.ids:
                self.ids[button_id].state = "normal"

    def set_focus_button(self, focused_button_id):
        self.clear_focus()
        if focused_button_id in self.ids:
            self.ids[focused_button_id].state = "down"

    def handle_on_enter(self):
        if self.current_button == 'upgrade_btn':
            self.on_upgrade_btn_click()
        elif self.current_button == 'rollback_btn':
            self.on_rollback_btn_click()
        elif self.current_button == 'back_btn':
            self.on_back_btn_click()
        
    def update_firmware_version(self, version: str):
        self.firmware_version = version
        Logger.debug(f"Update firmware version: {version}")

    def update_hardware_version(self, version: str):
        self.hardware_version = version
        Logger.debug(f"Update hardware version: {version}")

    def on_upgrade_btn_click(self):
        if self.is_upgrading:
            Logger.debug("Upgrade already in progress")
            return
        
        Logger.debug("Starting upgrade process...")
        self.is_upgrading = True

    def on_rollback_btn_click(self):
        Logger.debug("Rollback button clicked")
        pass

    def on_back_btn_click(self):
        Logger.debug("Back button clicked")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_option_screen()

