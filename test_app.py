from kivy.app import App
from kivy.uix.label import Label


from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '240')



class TestApp(App):
    def build(self):
        return Label(text="Hello, Kivy")



if __name__=="__main__":
    
    from kivy.core.window import Window
    print(f"window size: {Window.size}")
    TestApp().run()
