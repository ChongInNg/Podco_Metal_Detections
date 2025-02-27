
from kivy.uix.popup import Popup
from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate
from config.config import ConfigManager

class FlippedPopup(Popup):
    def __init__(self, **kwargs):
        super(FlippedPopup, self).__init__(**kwargs)
        self.apply_flip_transformation()

    def apply_flip_transformation(self):
        if ConfigManager.instance().is_flip_screen():
            with self.canvas.before:
                PushMatrix()
                Scale(-1, -1, 1)
                Translate(-self.width, -self.height, 0)
            with self.canvas.after:
                PopMatrix()

    def on_size(self, *args):
        if ConfigManager.instance().is_flip_screen():
            self.canvas.before.clear()
            self.canvas.after.clear()
            self.apply_flip_transformation()

    def init_attributes(self, 
            title: str, 
            title_size:str="20sp",
            size_hint=(None, None),
            size=(320, 240),
            auto_dismiss=False
        ):
        self.title_size = title_size
        self.size_hint = size_hint
        self.size = size
        self.title = title
        self.auto_dismiss = auto_dismiss