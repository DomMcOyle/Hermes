from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager


class MainWindow(Screen):
    pass

class RecapWindow(Screen):
    pass

class ProgressWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("starting_window.kv")

class BaseApp(App):
    def build(self):
        return kv

if __name__ == '__main__':
    BaseApp().run()
