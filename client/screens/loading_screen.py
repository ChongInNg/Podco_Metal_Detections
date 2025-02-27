from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from screens.flip_popup import FlippedPopup

class LoadingScreen(FlippedPopup):
    def __init__(self, message="Loading...", timeout=3, on_timeout_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.init_attributes(title="Please Wait")

        self.timeout = timeout
        self.on_timeout_callback = on_timeout_callback
        self.timeout_event = None

        layout = BoxLayout(orientation="vertical", padding=0, spacing=10)
        self.message_label = Label(text=message, halign="center", valign="middle", size_hint=(1, 1), font_size=20)
        self.message_label.bind(size=self.message_label.setter("text_size"))
        self.loading_icon = AsyncImage(source="assets/loading.gif", size_hint=(1, 0.7))

        layout.add_widget(self.message_label)
        layout.add_widget(self.loading_icon)

        self.content = layout
        self.current_state = "dismiss"

    def reset_state(self):
        self.current_state = "dismiss"

    def update_message(self, new_message):
        self.message_label.text = new_message

    def show(self):
        self.handle_open()
        self.timeout_event = Clock.schedule_once(self._on_timeout, self.timeout)

    def hide(self):
        if self.timeout_event:
            Clock.unschedule(self.timeout_event)
            self.timeout_event = None
        self.handle_dismiss()

    def _on_timeout(self, dt):
        self.hide()
        if self.on_timeout_callback:
            self.on_timeout_callback()

    def handle_dismiss(self):
        self.dismiss()
        self.current_state = "dismiss"

    def handle_open(self):
        super().open()
        self.current_state = "opened"
    
    def is_showing(self) -> bool:
        return self.current_state == "opened"
