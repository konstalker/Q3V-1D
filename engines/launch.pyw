import os
import sys
import shlex
import subprocess
from threading import Thread

from upd_tools import *
from gui_tools import App, Page, RedirectToText, check_worker


class Terminal(Page):
    def setup(self):
        text = self.text(size=(800, 400))
        sys.stdout = RedirectToText(text)


app = App(title='Q3V#1D', icon='./icons/b3.png', size=(800, 400))
app.page_area(size=(800, 400), pos=(0, 0))
app.register(Terminal, 'terminal')


def launch(args='+set fs_homepath "../baseq3/mods" +set fs_basepath "../" +set fs_game "osp"'):
    vk_engine, ogl_engine = None, False
    if os.path.exists('./engine.txt'):
        with open('./engine.txt') as engine_file:
            engine_conf = engine_file.read().split('\n')
            if len(engine_conf) == 2:
                vk_engine, ogl_engine = engine_conf[:2]
            else:
                vk_engine, ogl_engine = engine_conf[0], False

    has_vulkan = (
        os.path.exists(os.path.expandvars(r'%SystemRoot%\System32\vulkan-1.dll')) or
        os.path.exists(os.path.expandvars(r'%SystemRoot%\SysWOW64\vulkan-1.dll'))
    )

    engine = vk_engine if (has_vulkan or not ogl_engine) else ogl_engine

    if c_info.s_data == 'linux':
        os.system(f'chmod +x {engine}')

    subprocess.call([engine] + shlex.split(args))


if __name__ == "__main__":
    thread = Thread(target=autoupdate)
    thread.start()
    check_worker(app, thread, 100, app.qapp.quit)
    app.run()      # блокирует выполнение, пока окно открыто
    launch()       # выполнится только после закрытия окна (см. правку ниже)
