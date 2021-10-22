import sys
from datetime import datetime

class Log:
    def __init__(self, exception):
        f = open("log.txt", mode='a')
        f.write(str(datetime.now()) + ": ")
        f.write("Line " + str(sys.exc_info()[-1].tb_lineno) + " of ")
        f.write(str(sys.exc_info()[-1].tb_frame.f_code.co_filename) + '\n')
        f.write(type(exception).__name__ + ": ")
        f.write(str(exception) + "\n")
        f.close()

