from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty

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
            self.manager.current = "main"
        return super().on_touch_down(touch)
    
    def handle_direction(self, direction):
        if direction != "center":
            print(f"Not support: {direction} in logo screen")
            return
        self.manager.current = "main"
        print(f"logo screen handle {direction}")
