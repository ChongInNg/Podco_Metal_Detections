from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from screens.flip_popup import FlippedPopup
from log.logger import Logger

class ProgressPopup(FlippedPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_attributes(title="Progress")

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.status_label = Label(
            text="Processing...",
            halign="center",
            valign="middle",
            font_size=18,
            size_hint_y=0.3
        )
        self.status_label.bind(size=self.status_label.setter("text_size"))

        self.progress_value_label = Label(
            text="0/100",
            halign="center",
            valign="middle",
            font_size=22,
            size_hint_y=0.3,
            color=(0.3, 0.8, 1, 1),
            bold=True
        )
        self.progress_value_label.bind(size=self.progress_value_label.setter("text_size"))

        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=0.4
        )

        layout.add_widget(self.status_label)
        layout.add_widget(self.progress_value_label)
        layout.add_widget(self.progress_bar)

        self.content = layout
        self.current_state = "dismiss"

    def set_title(self, title: str):
        self.title = title
        Logger.debug(f"Set title: {title}")

    def update_status(self, status_text: str):
        self.status_label.text = status_text
        Logger.debug(f"Progress popup status updated: {status_text}")

    def update_progress_value(self, current: int, total: int):
        self.progress_value_label.text = f"{current}/{total}"
        Logger.debug(f"Progress popup value updated: {current}/{total}")

    def update_progress_percentage(self, percentage: int):
        self.progress_value_label.text = f"{percentage}%"
        Logger.debug(f"Progress popup percentage updated: {percentage}%")

    def update_progress_bar(self, current: int, total: int):
        self.progress_bar.max = total
        self.progress_bar.value = current
        Logger.debug(f"Progress bar updated: {current}/{total}")

    def update_all(self, status_text: str, current: int, total: int):
        self.update_status(status_text)
        self.update_progress_value(current, total)
        self.update_progress_bar(current, total)

    def reset(self):
        self.title = "Progress"
        self.status_label.text = "Processing..."
        self.progress_value_label.text = "0/100"
        self.progress_bar.value = 0
        self.progress_bar.max = 100
        Logger.debug("Progress popup reset to initial state")

    def reset_state(self):
        self.current_state = "dismiss"

    def handle_dismiss(self):
        self.dismiss()
        self.reset_state()
        Logger.debug("Progress popup dismissed")

    def handle_open(self):
        self.open()
        self.current_state = "opened"
        Logger.debug("Progress popup opened")

    def is_showing(self) -> bool:
        return self.current_state == "opened"
