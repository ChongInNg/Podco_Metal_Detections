from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
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
            text="0%",
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

        self.confirm_button = Button(
            text="Confirm",
            size_hint_y=0.2,
            font_size=20
        )
        self.confirm_button.bind(on_release=self._on_confirm)

        layout.add_widget(self.status_label)
        layout.add_widget(self.progress_value_label)
        layout.add_widget(self.progress_bar)

        self.content = layout
        self.main_layout = layout
        self.current_state = "dismiss"
        self.error_state = False

    def set_title(self, title: str):
        self.title = title
        Logger.debug(f"Set title: {title}")

    def update_status(self, status_text: str):
        self.status_label.text = status_text
        Logger.debug(f"Progress popup status updated: {status_text}")

    def update_progress_value(self, current: int, total: int):
        percentage = int((current / total * 100)) if total > 0 else 0
        self.progress_value_label.text = f"{percentage}%"
        Logger.debug(f"Progress popup value updated: {percentage}% ({current}/{total})")

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

    def show_error_state(self, error_message: str):
        self.error_state = True
        self.status_label.text = error_message

        if self.progress_value_label in self.main_layout.children:
            self.main_layout.remove_widget(self.progress_value_label)
        if self.progress_bar in self.main_layout.children:
            self.main_layout.remove_widget(self.progress_bar)

        if self.confirm_button not in self.main_layout.children:
            self.main_layout.add_widget(self.confirm_button)

        self.confirm_button.state = "down"
        Logger.debug(f"Progress popup switched to error state: {error_message}")

    def show_normal_state(self):
        self.error_state = False
        if self.confirm_button in self.main_layout.children:
            self.main_layout.remove_widget(self.confirm_button)

        if self.progress_bar not in self.main_layout.children:
            self.main_layout.add_widget(self.progress_value_label)
            self.main_layout.add_widget(self.progress_bar)

        Logger.debug("Progress popup switched to normal state")

    def is_in_error_state(self) -> bool:
        return self.error_state

    def _on_confirm(self, instance):
        Logger.debug("Confirm button pressed in progress popup")
        self.handle_dismiss()

    def reset(self):
        self.title = "Progress"
        self.status_label.text = "Processing..."
        self.progress_value_label.text = "0%"
        self.progress_bar.value = 0
        self.progress_bar.max = 100
        self.error_state = False
        self.show_normal_state()
        Logger.debug("Progress popup reset to initial state")

    def reset_state(self):
        self.current_state = "dismiss"
        self.error_state = False

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
