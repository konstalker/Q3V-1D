import os
import sys
from threading import Thread

import download_tools as dt
from upd_tools import autoupdate
from bmods_tools import *
from base_methods import *

from gui_tools import *


class FDownload(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)
    
    def run(self):
        if not os.path.exists('../baseq3/mods/baseq3'):
            os.mkdir('../baseq3/mods/baseq3')
        if not os.path.exists('../baseq3/mods/osp/demos'):
            os.mkdir('../baseq3/mods/osp/demos')
        if not os.path.exists('./cache'):
            os.mkdir('./cache')
        bmod_conf.save()
        list(dt.download('./download_confs/base.dconf', skip=True))
        autoupdate()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    window.open_terminal()
    fdownload = FDownload()
    fdownload.finished.connect(window.close_terminal)
    fdownload.start()
    sys.exit(app.exec())
    