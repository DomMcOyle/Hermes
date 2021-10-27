from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from tkinter import filedialog, Tk
from Options import Options
import os


class MainWindow(Screen):
    def choose_file(self):
        Tk().withdraw()
        filepath = filedialog.askopenfilename(title="Scegli un File Excel",
                                              filetypes=[("Excel files", ".xlsx .xls")])
        # TODO eventualmente controllare liceità file excel
        app = App.get_running_app()
        app.options.set_exc_path(filepath)
        fnlabel = self.ids.filename_label
        fnlabel.text = os.path.basename(filepath)
        if self.ids.visualize_button.disabled:
            self.ids.visualize_button.disabled = False


    def preview_excel(self):
        app = App.get_running_app()
        os.startfile(app.options.get_exc_path())



class RecapWindow(Screen):
    pass


class ProgressWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class BaseApp(App):
    def build(self):
        self.options = Options()
        if not os.path.isfile(self.options.get_exc_path()):
            # if the file does not exist anymore, the path is disabled.
            self.options.set_exc_path("")
        return Builder.load_file("starting_window.kv")

    def stop(self, *args):
        self.options.dump_options()


if __name__ == '__main__':
    BaseApp().run()
