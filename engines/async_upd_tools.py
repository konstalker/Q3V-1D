import sys
from PyQt6 import QtCore

from upd_tools import *
from base_methods import *



class AutoUpdate(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)

    def run(self):
        forupd = get_updates()
        if "scripts" in forupd:
            update("scripts")
            if c_info.s_data == "windows":
                subprocess.Popen(["./python/setup_python.bat", "./launch.pyw"])
            else:
                os.system("chmod +x ./python/setup_python.sh")
                subprocess.Popen(["./python/setup_python.sh", "scripts/upd_tools.py"])
            sys.exit(0)
        autoupdate()
        self.result_ready.emit(True)

class Update(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)
    
    def __init__(self, repo_name):
        self.repo_name = repo_name
        super().__init__()

    def run(self):
        update(self.repo_name)
        if self.repo_name == "scrips":
            if c_info.s_data == "windows":
                subprocess.Popen(["./python/setup_python.bat", "./launch.pyw"])
            else:
                os.system("chmod +x ./python/setup_python.sh")
                subprocess.Popen(["./python/setup_python.sh", "scripts/upd_tools.py"])
            sys.exit(0)
        self.result_ready.emit(True)

class Remove(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)
    
    def __init__(self, repo_name):
        self.repo_name = repo_name
        super().__init__()

    def run(self):
        remove(self.repo_name)
        self.result_ready.emit(True)
