import os
import sys
from threading import Thread

import download_tools as dt
from upd_tools import autoupdate
from bmods_tools import *
from base_methods import *
from gui_tools import *


class Terminal(Page):
    def setup(self):
        text = self.text(size=(800, 400))
        sys.stdout = RedirectToText(text)
        
class LaunchPage(Page):
    def setup(self):
        self.button(
            'launch',
            callback=self.on_launch_clicked,
            size=(240, 50),
            alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.button(
            'metarena',
            callback=self.on_meta_clicked,
            size=(240, 50),
            alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.stretch()

    def on_launch_clicked(self):
        launch()
        exit()

    def on_meta_clicked(self):
        launch('+set fs_homepath "../baseq3/mods" +set fs_basepath "../" +set fs_game "osp" +set com_viewlog "0" +connect metarena.ru')
        exit()

app = App(title='Q3V#1D installer', icon='./icons/b3.png', size=(800, 400))
app.page_area(size=(800, 400), pos=(0, 0))
app.register(Terminal, 'terminal')
app.register(LaunchPage, 'launch')


def main():
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
    thread = Thread(target=main)
    app.show_page('terminal')
    thread.start()
    check_worker(app, thread, 100, lambda: app.show_page('launch'))
    app.run()
