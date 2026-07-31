import download_tools as dt
from upd_tools import autoupdate
from bmods_tools import *
import sys
from gui_tools import *
from threading import Thread
from base_methods import *


# set up window

class Terminal(Page):
    def setup(self):
        text = self.text(size=(800, 400))
        sys.stdout = RedirectToText(text)

app = App(title='Q3V#1D installer', icon='./icons/b3.png', size=(800, 400))
app.page_area(size=(800, 400), pos=(0, 0))
app.register(Terminal, 'terminal')

def main():
    # needed paths
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
    thread.start()
    check_worker(app, thread, 100, exit)
    app.run()
