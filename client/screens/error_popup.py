from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class ErrorPopup(Popup):
    def __init__(self, message="An error occurred!", **kwargs):
        super().__init__(size_hint=(None, None), size=(320, 240), title="Error", auto_dismiss=False, **kwargs)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.message_label = Label(text=message, halign="center", valign="middle")
        self.message_label.bind(size=self.message_label.setter("text_size"))

        self.ok_button = Button(text="OK", size_hint=(1, 0.5))
        self.ok_button.bind(on_release=self.handle_dismiss)
        self.ok_button.state = "down"

        layout.add_widget(self.message_label)
        layout.add_widget(self.ok_button)
        self.content = layout

        self.current_state = "dismiss"

    def reset_state(self):
        self.current_state = "dismiss"
        self.ok_button.state = "down"

    def update_message(self, new_message):
        self.message_label.text = new_message

    def on_left_pressed(self):
        print("ErrorPopup on_left_pressed")

    def on_right_pressed(self):
        print("ErrorPopup on_right_pressed")
    
    def handle_on_enter(self):
        self.handle_dismiss(self)
        print("ErrorPopup handle_on_enter")

    def handle_dismiss(self, instance):
        self.dismiss()
        self.current_state = "dismiss"

    def handle_open(self):
        self.open()
        self.current_state = "opened"

    def is_showing(self) -> bool:
        return self.current_state == "opened"
