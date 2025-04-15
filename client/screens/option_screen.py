from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, BooleanProperty
from log.logger import Logger

class OptionScreen(Screen):
    title = StringProperty('Main Menu')

    admin_button_ids = ["detection_btn", "calibration_btn", 
                "analyzer_btn", "status_btn", "setting_btn", "exit_btn"]
    
    user_button_ids = ["detection_btn", "calibration_btn", "status_btn",
                "setting_btn", "exit_btn"]
    
    def __init__(self, **kwargs):
        super(OptionScreen, self).__init__(**kwargs)
        self.button_ids = OptionScreen.user_button_ids
        self.build_ui()

    def build_ui(self):
        self.current_button = "detection_btn"
        self.highlight_color = (0.196, 0.643, 0.808, 1)
        self.default_backgroud_color = (0,0,0,0)
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=2,
            padding=0
        )
        
        with main_layout.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_canvas, size=self.update_canvas)
        
        self.grid_layout = GridLayout(
            cols=2,
            rows=3,
            spacing=25,
            padding=[10,25,10,10],
            size_hint_y=0.9
        )
        with self.grid_layout.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            Rectangle(pos=self.grid_layout.pos, size=self.grid_layout.size)
        self.grid_layout.bind(pos=self.update_canvas, size=self.update_canvas)

        # Detections
        self.detection_layout = self._create_detections_layout() 
        # Calibrations
        self.calibration_layout = self._create_calbration_layout()
       
        # Analyzer
        self.analyzer_layout = self._create_analyzer_layout()
       
        # Settings
        self.setting_layout = self._create_setting_layout()
        
        # Status
        self.status_layout = self._create_status_layout()
       
        # Exit
        self.exit_layout = self._create_exit_layout()
       
        main_layout.add_widget(self.grid_layout)
        self.add_widget(main_layout)

    def get_title(self):
        return self.title
    
    def reset_data(self):
        self.current_button = "detection_btn"
        self.set_focus_button(self.current_button)
    
    def set_focus(self, is_up: bool):
        if is_up:
            current_index = self.button_ids.index(self.current_button)
            new_index = (current_index - 1) % len(self.button_ids)
            self.current_button = self.button_ids[new_index]
            self.set_focus_button(self.current_button)
        else: #down
            current_index = self.button_ids.index(self.current_button)
            new_index = (current_index + 1) % len(self.button_ids)
            self.current_button = self.button_ids[new_index]
            self.set_focus_button(self.current_button)
    
    def clear_focus(self):
        for button_id in self.button_ids:
            button = self.ids[button_id]
            button.background_color = self.default_backgroud_color

    def set_focus_button(self, focused_button_id):
        # Reset all buttons to "normal" state
        self.clear_focus()

        focused_button = self.ids[focused_button_id]
        focused_button.background_color = self.highlight_color

    def handle_on_enter(self):
        if self.current_button == "detection_btn":
            self.on_detection_btn_click()
        elif self.current_button == "calibration_btn":
            self.on_calibration_btn_click()
        elif self.current_button == "analyzer_btn":
            self.on_analyzer_btn_click()
        elif self.current_button == "setting_btn":
            self.on_setting_btn_click()
        elif self.current_button == "status_btn":
            self.on_status_btn_click()
        elif self.current_button == "exit_btn":
            self.on_exit_btn_click()
        else:
            Logger.debug("No button selected")
            self.clear_focus()

    def update_canvas(self, instance, value):
        for instruction in instance.canvas.before.get_group(None):
            if isinstance(instruction, Rectangle):
                instruction.pos = instance.pos
                instruction.size = instance.size

    def _create_detections_layout(self)->BoxLayout:
        detection_layout = self._create_layout("Detections")

        detection_image = self._create_image("assets/detection_icon.png")
        detection_btn = self._create_button("Detections")
        detection_btn.bind(on_release=self.on_detection_btn_click)
        self.ids['detection_btn'] = detection_btn
        detection_layout.add_widget(detection_image)
        detection_layout.add_widget(detection_btn)
        return detection_layout

    def _create_calbration_layout(self)->BoxLayout:
        calibration_layout = self._create_layout("Calibrations")
        calibration_image = self._create_image("assets/calibration_icon.png")
        calibration_btn = self._create_button("Calibrations")
        calibration_btn.bind(on_release=self.on_calibration_btn_click)
        self.ids['calibration_btn'] = calibration_btn
        calibration_layout.add_widget(calibration_image)
        calibration_layout.add_widget(calibration_btn)
        return calibration_layout
    
    def _create_analyzer_layout(self)->BoxLayout:
        analyzer_layout = self._create_layout("Analyzer")
        analyzer_image = self._create_image("assets/analyzer_icon.png")
        analyzer_btn = self._create_button("Analyzer")
        analyzer_btn.bind(on_release=self.on_analyzer_btn_click)
        self.ids['analyzer_btn'] = analyzer_btn
        analyzer_layout.add_widget(analyzer_image)
        analyzer_layout.add_widget(analyzer_btn)
        return analyzer_layout
    
    def _create_setting_layout(self)->BoxLayout:
        setting_layout = self._create_layout("Settings")
        setting_image = self._create_image("assets/setting_icon.png")
        setting_btn = self._create_button("Settings")
        setting_btn.bind(on_release=self.on_setting_btn_click)
        self.ids['setting_btn'] = setting_btn
        setting_layout.add_widget(setting_image)
        setting_layout.add_widget(setting_btn)
        return setting_layout
    
    def _create_status_layout(self)->BoxLayout:
        status_layout = self._create_layout("Status")
        status_image = self._create_image("assets/status_icon.png")
        status_btn = self._create_button("Status")
        status_btn.bind(on_release=self.on_status_btn_click)
        self.ids['status_btn'] = status_btn
        status_layout.add_widget(status_image)
        status_layout.add_widget(status_btn)
        return status_layout
    
    def _create_exit_layout(self)->BoxLayout:
        exit_layout = self._create_layout("Exit")
        exit_image = self._create_image("assets/exit_icon.png")
        exit_btn = self._create_button("Exit")
        exit_btn.bind(on_release=self.on_exit_btn_click)
        self.ids['exit_btn'] = exit_btn
        exit_layout.add_widget(exit_image)
        exit_layout.add_widget(exit_btn)
        return exit_layout
    
    def _create_layout(self, name: str)->BoxLayout:
        return BoxLayout(
            orientation='vertical',
            spacing=2,
            size_hint_y=None,
            height=80,
            opacity=1,
            disabled=False
        )

    def _create_image(self, source: str)->Image:
        return Image(
            source=source,
            size_hint=(None, None),
            size=(64, 64),
            fit_mode='contain',
            pos_hint={'center_x': 0.5}
        )

    def _create_button(self, text: str)->Button:
        return Button(
            text=text,
            font_size="12sp",
            size_hint_y=None,
            height=30,
            background_normal='',
            background_color=(0, 0, 0, 0)
        )

    def navigate_to_screen(self, screen_name):
        app = App.get_running_app()
        stack_widget = app.root.get_screen("main").ids.stack_widget
        stack_widget.change_to_screen_name(screen_name)
        Logger.debug(f"Navigating to {screen_name}")

    def on_detection_btn_click(self, *args):
        self.navigate_to_screen("detection")

    def on_calibration_btn_click(self, *args):
        self.navigate_to_screen("calibration")

    def on_analyzer_btn_click(self, *args):
        self.navigate_to_screen("analyzer")

    def on_setting_btn_click(self, *args):
        self.navigate_to_screen("setting")

    def on_status_btn_click(self, *args):
        self.navigate_to_screen("status")

    def on_exit_btn_click(self, *args):
        App.get_running_app().switch_to_logo_screen()

    def update_ui_when_admin_login(self):
        self.grid_layout.clear_widgets()
        self.grid_layout.add_widget(self.detection_layout)
        self.grid_layout.add_widget(self.calibration_layout)
        self.grid_layout.add_widget(self.analyzer_layout)
        self.grid_layout.add_widget(self.status_layout)
        self.grid_layout.add_widget(self.setting_layout)
        self.grid_layout.add_widget(self.exit_layout)

        self.reset_data()

    def update_ui_when_user_login(self):
        self.grid_layout.clear_widgets()
        self.grid_layout.add_widget(self.detection_layout)
        self.grid_layout.add_widget(self.calibration_layout)
        self.grid_layout.add_widget(self.status_layout)
        self.grid_layout.add_widget(self.setting_layout)
        self.grid_layout.add_widget(self.exit_layout)
        
        self.reset_data()