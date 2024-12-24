from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_file("kv/logo_screen.kv")

class LogoScreen(Screen):
    def on_touch_down(self, touch):
       
        if self.collide_point(touch.x, touch.y):
            self.manager.current = "main"
        return super().on_touch_down(touch)
