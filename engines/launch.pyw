import os
import sys
import shlex
import subprocess
from threading import Thread

from upd_tools import *
from gui_tools import *


app = App(title='Q3V#1D', icon='./icons/b3.png', size=(800, 400))
app.page_area(size=(800, 400), pos=(0, 0))


if __name__ == "__main__":
    thread = Thread(target=autoupdate)
    thread.start()
    check_worker(app, thread, 100, app.qapp.quit)
    launch()       # выполнится только после закрытия окна (см. правку ниже)
