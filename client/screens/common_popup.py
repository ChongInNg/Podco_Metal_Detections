from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from screens.flip_popup import FlippedPopup
from log.logger import Logger

class CommonPopup(FlippedPopup):
    def __init__(self, message="An error occurred!", **kwargs):
        super().__init__(**kwargs)
        self.init_attributes(title="Title")

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.message_label = Label(text=message, halign="center", valign="middle", font_size=20)
        self.message_label.bind(size=self.message_label.setter("text_size"))

        self.ok_button = Button(text="OK", size_hint=(1, 0.5), font_size=20)
        self.ok_button.bind(on_release=self.handle_dismiss)
        self.ok_button.state = "down"

        layout.add_widget(self.message_label)
        layout.add_widget(self.ok_button)
        self.content = layout

        self.current_state = "dismiss"

    def update_title(self, tilte: str):
        self.title = tilte

    def reset_state(self):
        self.current_state = "dismiss"
        self.ok_button.state = "down"

    def update_message(self, new_message: str):
        self.message_label.text = new_message

    def on_left_pressed(self):
        Logger.debug("CommonPopup no need to handle on_left_pressed")

    def on_right_pressed(self):
        Logger.debug("CommonPopup no need to handle on_right_pressed")
    
    def handle_on_enter(self):
        self.handle_dismiss(self)
        Logger.debug("CommonPopup handle_on_enter")

    def handle_dismiss(self, instance):
        self.dismiss()
        self.current_state = "dismiss"

    def handle_open(self):
        self.open()
        self.current_state = "opened"

    def is_showing(self) -> bool:
        return self.current_state == "opened"
