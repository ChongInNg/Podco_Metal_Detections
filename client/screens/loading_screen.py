from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.clock import Clock

class LoadingScreen(Popup):
    def __init__(self, message="Loading...", timeout=3, on_timeout_callback=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(320, 240), auto_dismiss=False, title="Please Wait", **kwargs)

        self.timeout = timeout
        self.on_timeout_callback = on_timeout_callback
        self.timeout_event = None

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.message_label = Label(text=message, halign="center", valign="middle", size_hint=(1, 0.3))
        self.message_label.bind(size=self.message_label.setter("text_size"))
        self.loading_icon = AsyncImage(source="assets/loading.gif", size_hint=(1, 0.7))

        layout.add_widget(self.message_label)
        layout.add_widget(self.loading_icon)

        self.content = layout

    def update_message(self, new_message):
        self.message_label.text = new_message

    def show(self):
        super().open()
        self.timeout_event = Clock.schedule_once(self._on_timeout, self.timeout)

    def hide(self):
        if self.timeout_event:
            Clock.unschedule(self.timeout_event)
            self.timeout_event = None
        self.dismiss()

    def _on_timeout(self, dt):
        self.hide()
        if self.on_timeout_callback:
            self.on_timeout_callback()
