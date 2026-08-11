import os
import sys
import shlex
import subprocess
from threading import Thread

from upd_tools import *
from gui_tools import *


class Get_Upd(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)
    modlist_failed = QtCore.pyqtSignal(str)

    def run(self):
        modlist = get_modlist()
        if modlist == False:
            self.modlist_failed.emit('Не удалось загрузить список модов')
            return
        updates = get_updates()
        self.result_ready.emit(bool(updates))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()

    aupd = Get_Upd()
    aupd.result_ready.connect(window.upd_status)
    aupd.modlist_failed.connect(
        lambda msg: (window.upd_status(False),
                     ToastNotification.show_warning(window.centralwidget, msg))
    )
    aupd.start()
    sys.exit(app.exec())
