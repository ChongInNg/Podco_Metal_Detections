from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file('kv/image_button.kv') 
class ImageButton(Button):
    source = StringProperty('')
