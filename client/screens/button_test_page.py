from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from log.logger import Logger

Builder.load_file("kv/button_test_page.kv")

class ButtonTestPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def reset_data(self):
        """Reset all button highlights"""
        self.reset_all_highlights()
        Logger.debug("Button test page reset_data")

    def reset_all_highlights(self):
        button_ids = ['left_btn', 'right_btn', 'up_btn', 'down_btn', 'enter_btn', 'cal_btn', 'bypass_btn']
        for btn_id in button_ids:
            if btn_id in self.ids:
                self.ids[btn_id].state = "normal"

    def highlight_button(self, direction):
        self.reset_all_highlights()

        button_map = {
            "left": "left_btn",
            "right": "right_btn",
            "up": "up_btn",
            "down": "down_btn",
            "center": "enter_btn",
            "left_right": "cal_btn",
            "up_down": "bypass_btn"
        }

        if direction in button_map:
            btn_id = button_map[direction]
            if btn_id in self.ids:
                self.ids[btn_id].state = "down"
                Logger.debug(f"Button test: {btn_id} highlighted (state=down)")

    