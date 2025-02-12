from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class ConfirmationPopup(Popup):
    def __init__(self, title="Confirm", message="Are you sure?", on_confirm_callback=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(320, 240), title=title, auto_dismiss=False, **kwargs)
        
        self.on_confirm_callback = on_confirm_callback

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.message_label = Label(text=message, halign="center", valign="middle")
        self.message_label.bind(size=self.message_label.setter("text_size"))

        button_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=0.3)

        cancel_button = Button(text="Cancel", size_hint_x=0.5)
        confirm_button = Button(text="Confirm", size_hint_x=0.5, background_color=(1, 0, 0, 1))

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)

        layout.add_widget(self.message_label)
        layout.add_widget(button_layout)

        self.content = layout

        cancel_button.bind(on_release=self.dismiss)
        confirm_button.bind(on_release=self._on_confirm)

    def _on_confirm(self, instance):
        self.dismiss()
        if self.on_confirm_callback:
            self.on_confirm_callback()
