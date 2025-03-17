from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from log.logger import Logger
from controller.role_manager import RoleManager

Builder.load_file("kv/logo_screen.kv")

class LogoScreen(Screen):
    title = StringProperty('')
    version = StringProperty('')

    def set_title(self, title: str):
        self.title = title

    def set_version(self, version: str):
        self.version = version

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            RoleManager.instance().login_as_user()
            App.get_running_app().switch_to_main_screen()
        return super().on_touch_down(touch)
    
    def handle_direction(self, direction):
        if direction != "center" and direction != "left_right":
            Logger.debug(f"Not support: {direction} in logo screen")
            return
        if direction == "left_right":
            if App.get_running_app().is_calibration_failed_popup_showing():
                Logger.debug("Calibration failed popup is showing, cannot login as admin now")
                return
            RoleManager.instance().login_as_admin()
            App.get_running_app().switch_to_main_screen()
        else:
            if App.get_running_app().is_calibration_failed_popup_showing():
                App.get_running_app().dismiss_calibration_failed_popup()
                return

            if RoleManager.instance().is_admin(): #it can not run here, because no idle when role is admin
                Logger.debug("Current role is admin, no need to handle enter signal")
                return
            RoleManager.instance().login_as_user()
            App.get_running_app().switch_to_main_screen()

        Logger.debug(f"logo screen handle {direction}")


