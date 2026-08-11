import os
import sys

import download_tools as dt
from upd_tools import autoupdate
from bmods_tools import *
from base_methods import *

from gui_tools import *


class FDownload(QtCore.QThread):
    result_ready = pyqtSignal(bool)
    
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

class MDownload(QtCore.QThread):
    result_ready = pyqtSignal(bool)
    
    def run(self):
        get_modlist()

def mdlist_check():
    window.upd_status(False)
    if not os.path.exists('./temp_files/modlist.json'):
        window.qerror('Internet connection error.')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_id = QFontDatabase.addApplicationFont("./ui/FiraCode-Regular.ttf")
    if font_id == -1:
        print("Ошибка: не удалось загрузить шрифт :/fonts/MyFont.ttf")
        # Можно поставить запасной шрифт
        family = "Arial"
    else:
        families = QFontDatabase.applicationFontFamilies(font_id)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()

    font_id = QFontDatabase.addApplicationFont("./ui/FiraCode-Regular.ttf")
    if font_id == -1:
        print("Ошибка: не удалось загрузить шрифт :/fonts/MyFont.ttf")
        # Можно поставить запасной шрифт
        family = "Arial"
    else:
        family = QFontDatabase.applicationFontFamilies(font_id)[0]

    window.terminal.set_font(family)
    
    window.show()
    window.open_terminal()
    fdownload = FDownload()
    mdownload = MDownload()
    mdownload.finished.connect(mdlist_check)
    fdownload.finished.connect(window.close_terminal)
    mdownload.start()
    fdownload.start()
    sys.exit(app.exec())
    