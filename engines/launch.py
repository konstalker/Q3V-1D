from base_methods import *
from upd_tools import *
from dmods_tools import *
import subprocess


def launch(args='+set fs_homepath "../baseq3/mods" +set fs_basepath "../" +set fs_game "osp"'):
    autoupdate()

    if os.path.exists('./engine.txt'):
        with open('./engine.txt') as engine_file:
            engine_conf = engine_file.read().split('\n')
            if len(engine_conf) == 2:
                vk_engine, ogl_engine = engine_conf[:2]
            else:
                vk_engine, ogl_engine = engine_conf[0], False

    if os.path.exists('%SystemRoot%/System32/vulkan-1.dll') or\
       os.path.exists('%SystemRoot%/SysWOW64/vulkan-1.dll') or\
       not ogl_engine:
        if c_info.s_data == 'linux':
            os.system(f'chmod +x {vk_engine}')
        subprocess.run([vk_engine, args])
    else:
        if c_info.s_data == 'linux':
            os.system(f'chmod +x {ogl_engine}')
        subprocess.run([ogl_engine, args])


if __name__ == "__main__":
    launch()
