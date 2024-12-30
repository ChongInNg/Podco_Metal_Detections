from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file("kv/analyzer_screen.kv")

class AnalyzerScreen(Screen):
    title = StringProperty('Analyzer')

    def reset_data(self):
        pass

    def get_title(self):
        return self.title