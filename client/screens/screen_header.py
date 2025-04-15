from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder
from log.logger import Logger
Builder.load_file('kv/screen_header.kv')

class ScreenHeader(BoxLayout):
    title = StringProperty('')
    show_back = BooleanProperty(False)
    show_next = BooleanProperty(False)
    server_status_image = StringProperty('assets/red_circle.png')

    # update button default state
    def on_kv_post(self, base_widget):
        self.server_status = 0
        self.update_btn_state()

    def update_header(self, title):
        self.title = title
        self.update_btn_state()

    def on_back_clicked(self):
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        
        stack_widget.handle_direction("left")

    def on_next_clicked(self):
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        
        stack_widget.handle_direction("right")
    
    def update_btn_state(self):
        if self.is_detection() or self.is_calibration() \
            or self.is_analyzer() or self.is_status():
            self.show_back = True
            self.show_next = True
        else:
            self.show_back = False
            self.show_next = False

        back_button = self.ids.back_button
        back_button.opacity = 1 if self.show_back else 0
        back_button.disabled = not self.show_back

        next_button = self.ids.next_button
        next_button.opacity = 1 if self.show_next else 0
        next_button.disabled = not self.show_next

    def is_detection(self):
        return self.title == "Detection"
    
    def is_calibration(self):
        return self.title == "Calibration"
    
    def is_analyzer(self):
        return self.title == "Analyzer"
    
    def is_option(self):
        return self.title == "Main Menu"
    
    def is_status(self):
        return self.title == "Status"
    
    def update_server_status(self, on: bool):
        if on:
            self.server_status = 1
            self.server_status_image = 'assets/green_circle.png'
            Logger.debug("Update to green status.")
        else:
            self.server_status = 0
            self.server_status_image = 'assets/red_circle.png'
            Logger.debug("Update to red status.")