from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle

class CustomSlider(Slider):
    HIGHLIGHT_slider_color = [0.196, 0.643, 0.808,1]
    DEFAULT_slider_color = [0.15, 0.15, 0.2, 1]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.highlight_state = False
        self.current_step = 1
        with self.canvas.before:
            self.bg_color = Color(0.15, 0.15, 0.2, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.change_color(CustomSlider.HIGHLIGHT_slider_color)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.change_color(CustomSlider.DEFAULT_slider_color)
        return super().on_touch_up(touch)

    def change_color(self, color):
        if color == CustomSlider.HIGHLIGHT_slider_color:
            self.highlight_state = True
        else:
            self.highlight_state = False
        self.bg_color.rgba = color
        self.canvas.ask_update() # need to force update

    def highlight_color(self):
        self.change_color(CustomSlider.HIGHLIGHT_slider_color)
    
    def reset_color(self):
        self.change_color(CustomSlider.DEFAULT_slider_color)

    def is_highlight(self)->bool:
        return self.highlight_state
    
    def increase_value(self):
        if self.value + self.current_step < self.max:
            self.value += self.current_step

    def decrease_value(self):
        if self.value - self.current_step > self.min:
            self.value -= self.current_step

    def reset_value(self, value=1500):
        self.value = value