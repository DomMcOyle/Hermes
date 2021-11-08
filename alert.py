from kivy.uix.popup import Popup
from kivy.uix.button import Button

class Alert(Popup):
    def fire(self, message, title):
        self.ids.alert_message.text = message
        self.title = title
        self.open()

    def fire_with_callback(self, message, title, callback):
        self.ids.alert_message.text = message
        self.title = title
        btn = Button(text='Ok')
        btn.pos_hint = {'y': 0.10, 'right': 0.60}
        btn.size_hint = (0.3, 0.2)
        btn.bind(on_release=callback)
        self.ids.popup_layout.add_widget(btn)
        self.open()


class TimeoutException(Exception):

    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)