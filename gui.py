from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from tkinter import filedialog, Tk
from Options import Options

options = None

class MainWindow(Screen):
    filename = ObjectProperty(None)
    def choose_file(self):
        Tk().withdraw()
        filepath = filedialog.askopenfilename(title="Scegli un File Excel",
                                              filetypes=[("Excel files", ".xlsx .xls")])

        options.set_exc_path(filepath)

class RecapWindow(Screen):
    pass

class ProgressWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("starting_window.kv")

class BaseApp(App):
    def build(self):
        options = Options()
        return kv

if __name__ == '__main__':
    BaseApp().run()
