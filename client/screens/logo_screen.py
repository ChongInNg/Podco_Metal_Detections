from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty

Builder.load_file("kv/logo_screen.kv")

class LogoScreen(Screen):
    title = StringProperty('')
    version = StringProperty('')

    def __init__(self, **kwargs):
        self.callback = None
        super().__init__(**kwargs)

    def set_title(self, title: str):
        self.title = title

    def set_version(self, version: str):
        self.version = version
    
    def set_recover_func(self, callback: callable):
        self.callback = callback

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.manager.current = "main"
            self.invoke_callback()
        return super().on_touch_down(touch)
    
    def handle_direction(self, direction):
        if direction != "center":
            print(f"Not support: {direction} in logo screen")
            return
        self.manager.current = "main"
        self.invoke_callback()
        print(f"logo screen handle {direction}")

    def invoke_callback(self):
        if self.callback != None:
            self.callback()

