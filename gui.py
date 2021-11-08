from kivy.config import Config

from kivy.app import App
from kivy.graphics.svg import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from tkinter import filedialog, Tk

from Options import Options
import os
import cv2

from alert import Alert
from debug import Log

from filereader import check_rows, acquire_numbers_from_excel_file

from kivy.config import Config
from hermes import send_to_list_in_thread, check_if_open, update_driver
import constants


Config.set("input", "mouse", "mouse,multitouch_on_demand")
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '600')


class MainWindow(Screen):

    def check_and_recap(self):
        app = App.get_running_app()
        if not os.path.isfile(app.options.get_exc_path()):
            Alert().fire("Non è stato selezionato un file valido", "Errore")
            return
        if self.ids.message_input.text == "" and len(app.file_paths) == 0:
            Alert().fire("Non è stato inserito del testo o immagini da inviare.", "Errore")
            return
        for image in app.file_paths:
            if not os.path.isfile(image):
                Alert().fire("L'immagine " + os.path.basename(image) + " non è stata trovata.", "Errore")
                return
        start_index = app.options.get_last_index() + 1
        exc_rows = check_rows(app.options.get_exc_path())
        if exc_rows < 1:
            Alert().fire("Il file selezionato è vuoto", "Errore")
            return
        if not self.ids.row_input.text == "":
            start_index = int(self.ids.row_input.text)
            if start_index < 1 or start_index > exc_rows:
                Alert().fire("L'indice non presenta un valore valido. (Il file selezionato ha " + str(exc_rows)
                             + " righe)", "Errore")
                return

        app.message_txt = self.ids.message_input.text

        next_window = self.manager.get_screen('recap')
        next_window.ids.message_label.text = app.message_txt
        next_window.ids.excel_label.text = app.options.get_exc_path()
        next_window.ids.index_label.text = str(start_index)
        imagelist = ""
        for i in app.file_paths:
            imagelist = imagelist + os.path.basename(i) + '\n'
        if not imagelist:
            imagelist = "Nessuna immagine selezionata"
        next_window.ids.image_label.text = imagelist

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
    def start_send(self):
        app = App.get_running_app()
        app.effective_starting_index = int(self.ids.index_label.text)-1
        next_window = self.manager.get_screen('progress')

        rows = check_rows(app.options.get_exc_path())
        next_window.ids.p_bar.max = rows - app.effective_starting_index
        next_window.ids.p_bar.value = 0
        next_window.ids.p_label.text = "Invio dei messaggi...  (" + str(next_window.ids.p_bar.max) + " numeri rimanenti)"

        if not os.path.isfile(app.options.get_exc_path()):
            Alert().fire("Il file contenente i numeri è stato spostato o rimosso.", "Errore")
            return

        if check_if_open("chrome.exe"):
            Alert().fire("Google Chrome è attualmente in uso. Chiudere ogni finestra del browser e riprovare.", "Errore")
            return

        self.manager.transition.direction = 'left'
        self.manager.current = 'progress'


class ProgressWindow(Screen):
    def rollback(self, index=None):
        app = App.get_running_app()

        if index is not None:
            next_window = self.manager.get_screen('recap')
            next_window.ids.index_label.text = str(index + 1)
            app.options.set_last_index(index)

        self.manager.transition.direction = 'right'
        self.manager.current = 'recap'
        app.pause_thread = False
        app.kill_thread = False

    def pause_send_thread(self):

        app = App.get_running_app()
        if not app.pause_thread:
            app.pause_thread = True
            self.ids.pause_button.text = "Riprendi"
        elif app.pause_thread:
            app.pause_thread = False
            self.ids.pause_button.text = "Pausa"

    def kill_thread_saving_index(self):
        app = App.get_running_app()
        app.kill_thread = True

    def get_pause_thread_value(self):
        app = App.get_running_app()
        return app.pause_thread

    def get_kill_thread_value(self):
        app = App.get_running_app()
        return app.kill_thread

    def send_loop(self):
        app = App.get_running_app()
        #self.ids.p_bar.value = 0
        #self.ids.p_bar.min = app.effective_starting_index
        self.ids.stop_button.text = "Stop"
        self.ids.stop_button.on_release = self.kill_thread_saving_index
        try:
            number_list, wrong_numbers = acquire_numbers_from_excel_file(app.options.get_exc_path())
        except:
            Alert().fire("Il file indicato non contiene numeri di telefono utilizzabili", "Errore")
            self.manager.transition.direction = 'right'
            self.manager.current = 'main'
            return
        send_to_list_in_thread(number_list, app.effective_starting_index, app.message_txt, app.file_paths, self)

    def update_progress_bar(self):
        self.ids.p_bar.value += 1
        remaining = int(self.ids.p_bar.max - self.ids.p_bar.value)
        self.ids.p_label.text = "Invio dei messaggi...  (" + str(remaining) + " numeri rimanenti)"

    def finalize_send(self, inexistent_number_found):
        self.ids.p_label.text = "Invio dei messaggi completato!"
        if inexistent_number_found:
            self.ids.p_label.text += '\n ATTENZIONE: alcuni numeri sono risultati inesistenti e sono stati salvati' \
                                     ' in un file di testo "Numeri inesistenti"'
        self.ids.pause_button.disabled = True
        self.ids.stop_button.text = "Indietro"
        self.ids.stop_button.on_release = self.rollback


class WindowManager(ScreenManager):
    pass

class BaseApp(App):
    def build(self):
        Window.clearcolor = (43 / 256, 60 / 256, 103 / 256, 1)
        update_driver()
        self.options = Options()
        self.img_paths = []
        self.current_image = 0
        self.file_paths = []
        self.message_txt = ""
        self.effective_starting_index = 0
        self.pause_thread = False
        self.kill_thread = False
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
    try:
        app = BaseApp()
        app.run()
    except Exception as e:
        app.options.dump_options()
        for elem in app.img_paths:
            if "_preview" in elem:
                os.remove(elem)
        Log(e)


