from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate
from kivy.uix.screenmanager import ScreenManager

class FlippedScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(FlippedScreenManager, self).__init__(**kwargs)
        self.apply_flip_transformation()

    def apply_flip_transformation(self):
        with self.canvas.before:
            PushMatrix()
            Scale(-1, -1, 1)
            Translate(-self.width, -self.height, 0)
        with self.canvas.after:
            PopMatrix()

    def on_size(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()
        self.apply_flip_transformation()