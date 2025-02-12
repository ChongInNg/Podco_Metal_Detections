from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider

class SetThresholdPopup(Popup):
    def __init__(self, on_confirm_callback=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(320, 240), title="Set Threshold", auto_dismiss=False, **kwargs)

        self.on_confirm_callback = on_confirm_callback
        self.current_threshold = 1500
        self.min_value = 500
        self.max_value = 2500

        popup_layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        self.label = Label(text=f"Threshold: {self.current_threshold}", font_size=14, size_hint_y=0.2)
        self.slider = Slider(min=self.min_value, max=self.max_value, value=self.current_threshold, size_hint_y=0.4)
        self.slider.bind(value=self.update_label)

        button_layout = BoxLayout(size_hint_y=0.5, spacing=5)
        cancel_button = Button(text="Cancel", size_hint=(0.5, 0.8), font_size=14)
        cancel_button.bind(on_press=self.dismiss)

        confirm_button = Button(text="Confirm", size_hint=(0.5, 0.8), font_size=14)
        confirm_button.bind(on_press=self.on_confirm)

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)

        popup_layout.add_widget(self.label)
        popup_layout.add_widget(self.slider)
        popup_layout.add_widget(button_layout)

        self.content = popup_layout

    def update_label(self, instance, value):
        self.label.text = f"Threshold: {int(value)}"

    def on_confirm(self, instance):
        self.dismiss()
        if self.on_confirm_callback:
            self.on_confirm_callback(int(self.slider.value))
        
