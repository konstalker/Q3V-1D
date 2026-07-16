import shlex

def launch(args='+set fs_homepath "../baseq3/mods" +set fs_basepath "../" +set fs_game "osp"'):
    autoupdate()

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

    subprocess.run([engine] + shlex.split(args))


if __name__ == "__main__":
    launch()