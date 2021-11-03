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
import constants


class MainWindow(Screen):

    img_paths = []
    current_image = 0

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
        self.update_carousel(filepaths)

    def update_carousel(self, filepaths):
        app = App.get_running_app()
        for elem in filepaths:
            if elem not in app.file_paths:
                app.file_paths.append(elem)
        images_paths = list(app.file_paths)

        name_list = []
        for elem in app.file_paths:
            name_list.append(elem.split("/")[-1])  # add to name list
            if name_list[-1].split(".")[1] == "mp4" or name_list[-1].split(".")[1] == "avi":
                frame = self.extract_frame(elem, 30)
                prev_name = "previews\\" + name_list[-1].replace(".mp4", "_preview.jpg")
                cv2.imwrite(prev_name, frame)
                images_paths.remove(elem)
                images_paths.append(prev_name)

        app.img_paths = images_paths
        if len(app.file_paths) > 0:
            self.ids.images_holder.source = images_paths[0]
        else:
            self.ids.images_holder.source = constants.place_holder_image
        app.current_image = 0

        names_to_show = str(name_list) \
            .replace("'", "").replace("[", "").replace("]", "").replace(",", "").replace(" ", "\n")
        self.ids.image_label.text = names_to_show

    def remove_pic(self):
        app = App.get_running_app()
        if len(app.file_paths) > 0:
            del app.file_paths[app.current_image]
            self.update_carousel(app.file_paths)

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
