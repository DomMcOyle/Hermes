from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from tkinter import filedialog, Tk
from Options import Options
import os
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class MainWindow(Screen):
    def choose_file(self):
        Tk().withdraw()
        filepath = filedialog.askopenfilename(title="Scegli un File Excel",
                                              filetypes=[("Excel files", ".xlsx .xls")])
        # TODO eventualmente controllare liceità file excel
        if filepath:
            app = App.get_running_app()
            app.options.set_exc_path(filepath)
            fnlabel = self.ids.filename_label
            fnlabel.text = os.path.basename(filepath)
            if self.ids.visualize_button.disabled:
                self.ids.visualize_button.disabled = False

    def preview_excel(self):
        app = App.get_running_app()
        path = app.options.get_exc_path()
        if os.path.isfile(path):
            os.startfile(path)
        else:
            Alert().fire('Il file "' + os.path.basename(path) + '" non è stato trovato nella cartella "' +
                        os.path.dirname(path) + '".', "Errore")


    def load_images(self):
        Tk().withdraw()
        filepaths = filedialog.askopenfilenames(title="Scegli le immagini da caricare",
                                               filetypes=[("Images", ".jpg .jpeg .png")])
        if len(filepaths) == 0:
            return
        name_list = []
        self.ids.carousel_holder.clear_widgets()
        for elem in filepaths:
            name_list.append(elem.split("/")[-1]) #add to name list
            self.ids.carousel_holder.add_widget(Image(source=elem)) #and to carousel

        names_to_show = str(name_list) \
            .replace("'", "").replace("[", "").replace("]", "").replace(",", "").replace(" ", "\n")
        image_label = self.ids.image_label
        image_label.text = os.path.basename(names_to_show)



class RecapWindow(Screen):
    pass


class ProgressWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class Alert(Popup):
    def fire(self, message, title):
        self.ids.alert_message.text = message
        self.title=title
        self.open()
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
