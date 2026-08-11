from PyQt6 import QtCore

from upd_tools import *
from base_methods import *



class AutoUpdate(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)

    def run(self):
        autoupdate()
        self.result_ready.emit(True)

class Update(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)
    
    def __init__(self, repo_name):
        self.repo_name = repo_name
        super().__init__()

    def run(self):
        update(self.repo_name)
        bmod_conf.save()
        self.result_ready.emit(True)

class Remove(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(bool)
    
    def __init__(self, repo_name):
        self.repo_name = repo_name
        super().__init__()

    def run(self):
        remove(self.repo_name)
        bmod_conf.save()
        self.result_ready.emit(True)
