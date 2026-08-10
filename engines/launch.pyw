import os
import sys
import shlex
import subprocess
from threading import Thread

from upd_tools import *
from gui_tools import *


class Get_modlist(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)

    def run(self):
        autoupdate()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    upd_checked = False
    for_upd = []
    window = MainWindow()
    window.show()
    window.open_terminal()
    aupd = Aupd()
    aupd.finished.connect(window.close_terminal)
    aupd.start()
    sys.exit(app.exec())
