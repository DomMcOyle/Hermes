from kivy.uix.popup import Popup


class Alert(Popup):
    def fire(self, message, title):
        self.ids.alert_message.text = message
        self.title = title
        self.open()


class TimeoutException(Exception):

    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)