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

        ok_button = Button(text="OK", size_hint=(1, 0.3))
        ok_button.bind(on_release=self.dismiss)

        layout.add_widget(self.message_label)
        layout.add_widget(ok_button)

        self.content = layout

    def update_message(self, new_message):
        self.message_label.text = new_message
