from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from tkinter import filedialog, Tk
from Options import Options
import os
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel

import cv2

from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button



class MainWindow(Screen):


    def check_and_recap(self):
        app = App.get_running_app()
        if not os.path.isfile(app.options.get_exc_path()):
            Alert().fire("Non è stato selezionato un file valido", "Errore")
        # check che le imagepath siano corrette
        # check che ci sia del testo
        # check che l'ìndice sia valido
        else:
            self.manager.transition.direction = 'left'
            self.manager.current = 'recap'

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
        filepaths = filedialog.askopenfilenames(title="Scegli le immagini/video da caricare",
                                                filetypes=[("Multimedia", ".jpg .jpeg .png .gif .mp4 .avi")])
        if len(filepaths) == 0:
            return

        images_paths = list(filepaths)

        name_list = []
        for elem in filepaths:
            name_list.append(elem.split("/")[-1])  # add to name list
            if name_list[-1].split(".")[1] == "mp4" or name_list[-1].split(".")[1] == "avi":
                frame = self.extract_frame(elem, 30)
                prev_name = "previews\\" + name_list[-1].replace(".mp4", "_preview.jpg")
                cv2.imwrite(prev_name, frame)
                images_paths.remove(elem)
                images_paths.append(prev_name)

        app = App.get_running_app()
        app.img_paths = images_paths
        self.ids.images_holder.source = images_paths[0]
        app.current_image = 0
        app.file_paths = list(filepaths)
        names_to_show = str(name_list) \
            .replace("'", "").replace("[", "").replace("]", "").replace(",", "").replace(" ", "\n")
        self.ids.image_label.text = names_to_show

    def extract_frame(self, elem, n_frame = 30):
        curr_video = cv2.VideoCapture(elem)
        curr_frame = 0
        while (curr_frame < n_frame):
            ret, frame = curr_video.read()
            curr_frame += 1
        return frame

    def next_pic(self):
        app = App.get_running_app()
        if len(app.img_paths) != 0:
            app.current_image = (app.current_image + 1) % len(app.img_paths)
            self.ids.images_holder.source = app.img_paths[app.current_image]

    def prev_pic(self):
        app = App.get_running_app()
        if len(app.img_paths) != 0:
            app.current_image = (app.current_image - 1) % len(app.img_paths)
            self.ids.images_holder.source = app.img_paths[app.current_image]


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
        self.img_paths = []
        self.current_image = 0
        self.file_paths = []
        if not os.path.isfile(self.options.get_exc_path()):
            # if the file does not exist anymore, the path is disabled.
            self.options.set_exc_path("")
        return Builder.load_file("starting_window.kv")

    def stop(self, *args):
        self.options.dump_options()
        for elem in self.img_paths:
            if "_preview" in elem:
                os.remove(elem)


if __name__ == '__main__':
    BaseApp().run()
