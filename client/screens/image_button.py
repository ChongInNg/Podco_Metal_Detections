from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

Builder.load_file('kv/image_button.kv') 
class ImageButton(ButtonBehavior, Image):
    source = StringProperty('')
