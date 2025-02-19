from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from screens.custom_slider import CustomSlider

class SetThresholdPopup(Popup):
    def __init__(self, on_confirm_callback=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(320, 240), title="Set Threshold", auto_dismiss=False, **kwargs)

        self.on_confirm_callback = on_confirm_callback
        self.current_threshold = 1500
        self.min_value = 500
        self.max_value = 2500

        popup_layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        self.label = Label(text=f"Threshold: {self.current_threshold}", size_hint_y=0.2)
        self.slider = CustomSlider(
            min=self.min_value, 
            max=self.max_value, 
            value=self.current_threshold, 
            size_hint_y=0.4,
        )
        self.slider.bind(value=self.update_label)

        button_layout = BoxLayout(size_hint_y=0.5, spacing=5)
        cancel_button = Button(text="Cancel", size_hint=(0.5, 0.8))
        cancel_button.bind(on_press=self.handle_dismiss)

        confirm_button = Button(
            text="Confirm", 
            size_hint=(0.5, 0.8), 
            background_color=(1, 0, 0, 1),
        )
        confirm_button.bind(on_press=self._on_confirm)

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)

        popup_layout.add_widget(self.label)
        popup_layout.add_widget(self.slider)
        popup_layout.add_widget(button_layout)

        self.content = popup_layout

        self.confirm_button = confirm_button
        self.cancel_button = cancel_button
        self.current_button = self.confirm_button
        self.current_state = "dismiss"

    def update_label(self, instance, value):
        self.label.text = f"Threshold: {int(value)}"

    def _on_confirm(self, instance):
        self.handle_dismiss(instance)
        if self.on_confirm_callback:
            self.on_confirm_callback(int(self.slider.value))
    
    def reset_state(self):
        self.current_state = "dismiss"
        self.current_button = self.confirm_button
        self.cancel_button.state = "normal"
        self.confirm_button.state = "normal"
        self.reset_slider_color()
        # self.slider.reset_value()
        
    def on_left_pressed(self):
        if self.slider.is_highlight():
            self.slider.decrease_value()
        else:
            self.current_button = self.cancel_button
            self.cancel_button.state = "down"
            self.confirm_button.state = "down"
        print("SetThresholdPopup on_left_pressed")

    def on_right_pressed(self):
        if self.slider.is_highlight():
            self.slider.increase_value()
        else:
            self.cancel_button.state = "normal"
            self.confirm_button.state = "normal"
            self.current_button = self.confirm_button
        print("SetThresholdPopup on_right_pressed")

    def handle_on_enter(self):
        if self.slider.is_highlight():
            print("Slider is highlight, SetThresholdPopup ingore to handle_on_enter.")
            return
        if self.current_button == self.confirm_button:
            self._on_confirm(self)
        else:
            self.handle_dismiss(self)  
        print("SetThresholdPopup handle_on_enter")

    def handle_dismiss(self, instance):
        self.dismiss()
        self.current_state = "dismiss"

    def handle_open(self):
        self.open()
        self.current_state = "opened"

    def is_showing(self) -> bool:
        return self.current_state == "opened"
    
    def highlight_slider(self):
        self.slider.highlight_color()
        print("highlight_slider.........")

    def reset_slider_color(self):
        self.slider.reset_color()
        print("reset_slider_color.........")

    def on_up_pressed(self):
        self.cancel_button.state = "normal"
        self.confirm_button.state = "down"
        self.current_button = None
        self.highlight_slider()

    def on_down_pressed(self):
        self.cancel_button.state = "normal"
        self.confirm_button.state = "normal"
        self.current_button = self.confirm_button
        self.reset_slider_color()
