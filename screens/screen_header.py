from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder

Builder.load_file('kv/screen_header.kv')

class ScreenHeader(BoxLayout):
    title = StringProperty('')
    show_back = BooleanProperty(False)
    show_next = BooleanProperty(False)

    # update button default state
    def on_kv_post(self, base_widget):
        self.update_btn_state()


    def update_header(self, title):
        self.title = title
        self.update_btn_state()

    def on_back_clicked(self):
        print(f"on_back_clicked {self.title}")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        
        if self.is_detection():
            stack_widget.change_screen("option")
        elif self.is_calibration():
            stack_widget.change_screen("detection")
        elif self.is_analyzer():
            stack_widget.change_screen("calibration")
        else:
            print(f"Cannot handle back button click on this tiltle: {self.title}")

    def on_next_clicked(self):
        print(f"on_next_clicked {self.title}")
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        
        if self.is_detection():
            stack_widget.change_screen("calibration")
        elif self.is_calibration():
            stack_widget.change_screen("analyzer")
        elif self.is_analyzer():
            stack_widget.change_screen("option")
        else:
            print(f"Cannot handle next button click on this tiltle: {self.title}")
    
    def update_btn_state(self):
        if self.is_detection():
            self.show_back = True
            self.show_next = True
        elif self.is_calibration():
            self.show_back = True
            self.show_next = True
        elif self.is_analyzer():
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
        return self.title == "Detections"
    
    def is_calibration(self):
        return self.title == "Calibrations"
    
    def is_analyzer(self):
        return self.title == "Analyzer"
    
    def is_option(self):
        return self.title == "Main Menu"