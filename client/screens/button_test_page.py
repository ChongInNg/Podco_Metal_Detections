from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
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

        self.hold_timer = None
        self.hold_start_time = 0
        self.hold_duration = 2.0
        self.progress_delay = 0.3
        self.trigger_back = False

    def on_kv_post(self, base_widget):
        self.bypass_btn = self.ids["bypass_btn"]
        self.cal_btn = self.ids["cal_btn"]
        self.progress_bar = self.ids.get("hold_progress_bar")
        self.progress_bar.opacity = 0
        self.progress_bar.value = 0
            
    def reset_data(self):
        self.reset_all_highlights()

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

        if direction == "center":
            # avoid trigger mulitple times until the release button event
            if self.hold_timer or self.trigger_back:
                return
            self.start_hold_timer()

    def release_button(self, direction):
        if direction in self.button_map:
            btn_id = self.button_map[direction]
            if btn_id in self.ids:
                self.ids[btn_id].state = "normal"
                Logger.debug(f"Button test: {btn_id} released (state=normal)")

        if direction == "center":
            self.cancel_hold_timer()
            if self.trigger_back:
                self.handle_trigger_back()
            else:
                self.progress_bar.opacity = 0
                self.progress_bar.value = 0

    def start_hold_timer(self):
        self.hold_start_time = Clock.get_time()
        self.hold_timer = Clock.schedule_interval(self.update_hold_progress, 0.05)

    def cancel_hold_timer(self):
        if self.hold_timer:
            self.hold_timer.cancel()
            self.hold_timer = None
        Logger.debug("Hold timer cancelled")

    def update_hold_progress(self, dt):
        elapsed_time = Clock.get_time() - self.hold_start_time
        if elapsed_time >= self.progress_delay:
            if self.progress_bar.opacity == 0:
                self.progress_bar.opacity = 1
                Logger.debug("Progress bar shown")

            progress = min((elapsed_time / self.hold_duration) * 100, 100)
            self.progress_bar.value = progress

        if elapsed_time >= self.hold_duration:
            self.cancel_hold_timer()
            self.trigger_back = True
            return False

    def handle_trigger_back(self):
        self.progress_bar.opacity = 0
        self.progress_bar.value = 0
        self.trigger_back = False

        from kivy.app import App
        app = App.get_running_app()
        setting_screen = app.main_screen.get_stack_widget().get_setting_screen()
        setting_screen.switch_to_settings_main()

    def highlight_bypass_button(self):
        self.bypass_btn.state = "down"

    def normal_bypass_button(self):
        self.bypass_btn.state = "normal"

    def highlight_cal_button(self):
        self.cal_btn.state = "down"

    def normal_cal_button(self):
        self.cal_btn.state = "normal"