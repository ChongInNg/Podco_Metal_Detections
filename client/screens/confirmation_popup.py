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

        self.cancel_button = Button(text="Cancel", size_hint_x=0.5)
        self.confirm_button = Button(text="Confirm", size_hint_x=0.5, background_color=(1, 0, 0, 1))

        button_layout.add_widget(self.cancel_button)
        button_layout.add_widget(self.confirm_button)

        layout.add_widget(self.message_label)
        layout.add_widget(button_layout)

        self.content = layout

        self.cancel_button.bind(on_release=self.handle_dismiss)
        self.confirm_button.bind(on_release=self._on_confirm)
        self.current_button = self.confirm_button
        
        self.current_state = "dismiss"

    def reset_state(self):
        self.current_state = "dismiss"
        self.current_button = self.confirm_button
        self.cancel_button.state = "normal"
        self.confirm_button.state = "normal"

    def _on_confirm(self, instance):
        self.handle_dismiss()
        if self.on_confirm_callback:
            self.on_confirm_callback()

    def on_left_pressed(self):
        self.current_button = self.cancel_button
        self.cancel_button.state = "down"
        self.confirm_button.state = "down"
        print("ConfirmationPopup on_left_pressed")

    def on_right_pressed(self):
        self.cancel_button.state = "normal"
        self.confirm_button.state = "normal"
        self.current_button = self.confirm_button
        print("ConfirmationPopup on_right_pressed")
    
    def handle_on_enter(self):
        if self.current_button == self.confirm_button:
            self._on_confirm(self)
        else:
            self.handle_dismiss()  
        print("ConfirmationPopup handle_on_enter")

    def handle_dismiss(self):
        self.dismiss()
        self.current_state = "dismiss"

    def handle_open(self):
        self.open()
        self.current_state = "opened"

    def is_showing(self) -> bool:
        return self.current_state == "opened"