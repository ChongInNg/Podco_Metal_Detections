from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_file("kv/logo_screen.kv")

class LogoScreen(Screen):
    def on_touch_down(self, touch):
        # Check if touch is on the image area (since the image covers the screen)
        if self.collide_point(touch.x, touch.y):
            # Go to the main screen when clicked
            self.manager.current = "main"
        return super().on_touch_down(touch)
