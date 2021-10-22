import configparser as cp

OPTIONS_PATH = "op.conf"
CONF_SECTION = "CONFIGURATION"
class Options:
    def __init__(self):
        parser = cp.ConfigParser()
        parser.read(OPTIONS_PATH)
        self.exc_path = parser[CONF_SECTION].get("excel_path")
        self.msg_timer = int(parser[CONF_SECTION].get("msg_timer"))
        self.last_index = int(parser[CONF_SECTION].get("last_index"))

    def get_exc_path(self):
        return self.exc_path

    def get_msg_timer(self):
        return self.msg_timer

    def get_last_index(self):
        return self.last_index

    def set_exc_path(self, path):
        self.exc_path = path

    def set_msg_timer(self, time_in_seconds):
        self.msg_timer = time_in_seconds

    def set_last_index(self, index):
        self.last_index = index

    def dump_options(self):
        parser = cp.ConfigParser()
        parser.read(OPTIONS_PATH)
        parser.set(CONF_SECTION, "excel_path", self.exc_path)
        parser.set(CONF_SECTION, "msg_timer", str(self.msg_timer))
        parser.set(CONF_SECTION, "last_index", str(self.last_index))
        with open(OPTIONS_PATH, 'w') as configfile:
            parser.write(configfile)
        configfile.close()

