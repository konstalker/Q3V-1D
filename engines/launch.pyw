if __name__ == "__main__":
    try:
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
                
        
        app = QApplication(sys.argv)
        
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
    
        aupd = Get_Upd()
        aupd.result_ready.connect(window.upd_status)
        aupd.modlist_failed.connect(
            lambda msg: (window.upd_status(False),
                        ToastNotification.show_warning(window.centralwidget, msg))
        )
        aupd.start()
        sys.exit(app.exec())
        
    except Exception as error:
        from base_methods import show_error
        
        message = f"{type(error).__name__}: {error}"
    
        show_error(message, lambda: update("scripts"))
