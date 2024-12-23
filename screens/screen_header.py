from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder

Builder.load_file('kv/screen_header.kv')
class ScreenHeader(BoxLayout):
    title = StringProperty('')
    show_back = BooleanProperty(True)
