from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from log.logger import Logger

Builder.load_file("kv/button_test_page.kv")

class ButtonTestPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_map = {
            "left": "left_btn",
            "right": "right_btn",
            "up": "up_btn",
            "down": "down_btn",
            "center": "enter_btn",
        }
        self.button_ids = ['left_btn', 'right_btn', 'up_btn', 'down_btn', 'enter_btn']
        

    def on_kv_post(self, base_widget):
        self.bypass_btn = self.ids["bypass_btn"]
        self.cal_btn = self.ids["cal_btn"]

    def reset_data(self):
        self.reset_all_highlights()
        Logger.debug("Button test page reset_data")

    def reset_all_highlights(self):
        for btn_id in self.button_ids:
            if btn_id in self.ids:
                self.ids[btn_id].state = "normal"

    def highlight_button(self, direction):
        self.reset_all_highlights()

        if direction in self.button_map:
            btn_id = self.button_map[direction]
            if btn_id in self.ids:
                self.ids[btn_id].state = "down"
                Logger.debug(f"Button test: {btn_id} highlighted (state=down)")

    def release_button(self, direction):
        if direction in self.button_map:
            btn_id = self.button_map[direction]
            if btn_id in self.ids:
                self.ids[btn_id].state = "normal"
                Logger.debug(f"Button test: {btn_id} released (state=normal)")

    def highlight_bypass_button(self):
        self.bypass_btn.state = "down"

    def normal_bypass_button(self):
        self.bypass_btn.state = "normal"
