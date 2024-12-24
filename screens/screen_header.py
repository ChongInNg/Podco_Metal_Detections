from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder

Builder.load_file('kv/screen_header.kv')

class ScreenHeader(BoxLayout):
    title = StringProperty('')
    show_back = BooleanProperty(True)
    show_next = BooleanProperty(True)

    def update_header(self, title, show_back):
        self.title = title
        self.show_back = show_back

    def on_back_clicked(self):
        print(f"on_back_clicked {self.title}")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        
        if self.title == "Detections":
            stack_widget.change_screen("option")
        elif self.title == "Calibrations":
            stack_widget.change_screen("detection")
        elif self.title == "Analyzer":
            stack_widget.change_screen("calibration")
        else:
            pass

    def on_next_clicked(self):
        print(f"on_next_clicked {self.title}")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        
        if self.title == "Detections":
            stack_widget.change_screen("calibration")
        elif self.title == "Calibrations":
            stack_widget.change_screen("analyzer")
        elif self.title == "Analyzer":
            stack_widget.change_screen("option")
        else:
            pass
