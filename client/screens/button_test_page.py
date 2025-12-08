from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivy.lang import Builder
from log.logger import Logger

Builder.load_file("kv/button_test_page.kv")

class ButtonTestPage(Screen):
    # Button highlight states
    left_highlighted = BooleanProperty(False)
    right_highlighted = BooleanProperty(False)
    up_highlighted = BooleanProperty(False)
    down_highlighted = BooleanProperty(False)
    enter_highlighted = BooleanProperty(False)
    cal_highlighted = BooleanProperty(False)
    bypass_highlighted = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def reset_data(self):
        """Reset all button highlights"""
        self.reset_all_highlights()
        Logger.debug("Button test page reset_data")

    def reset_all_highlights(self):
        """Reset all button highlight states"""
        self.left_highlighted = False
        self.right_highlighted = False
        self.up_highlighted = False
        self.down_highlighted = False
        self.enter_highlighted = False
        self.cal_highlighted = False
        self.bypass_highlighted = False

    def highlight_button(self, direction):
        """Highlight a button based on direction input"""
        # Reset all highlights first
        self.reset_all_highlights()

        # Highlight the corresponding button
        if direction == "left":
            self.left_highlighted = True
            Logger.debug("Button test: LEFT highlighted")
        elif direction == "right":
            self.right_highlighted = True
            Logger.debug("Button test: RIGHT highlighted")
        elif direction == "up":
            self.up_highlighted = True
            Logger.debug("Button test: UP highlighted")
        elif direction == "down":
            self.down_highlighted = True
            Logger.debug("Button test: DOWN highlighted")
        elif direction == "center":
            self.enter_highlighted = True
            Logger.debug("Button test: ENTER highlighted")
        elif direction == "left_right":
            self.cal_highlighted = True
            Logger.debug("Button test: CAL highlighted")
        elif direction == "up_down":
            self.bypass_highlighted = True
            Logger.debug("Button test: BYPASS highlighted")

    def on_back_pressed(self):
        """Handle back button press - return to settings main"""
        from kivy.app import App
        app = App.get_running_app()
        setting_screen = app.root.get_screen("main").ids.stack_widget.get_setting_screen()
        setting_screen.switch_to_settings_main()
        Logger.debug("Button test page: back pressed")

    def handle_on_enter(self):
        """Handle enter button - exit button test"""
        self.on_back_pressed()
        Logger.debug("Button test page: handle_on_enter")
