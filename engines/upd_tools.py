import shutil
from sys import version
import zipfile
import os

import download_tools as dt
from base_methods import caption, furl, c_info

from dmods_tools import dmod_conf


def update(repo_name):
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    modlist = {}
    dt.downloader(furl('[RURL]index.modlist'), "./temp_files/", "modlist.txt", skip=True)
    with open("./temp_files/modlist.txt", 'r') as f:
        for x in f.read().split('\n'):
            mod = list(x.split(';'))

            if mod[0] != repo_name:
                continue
            
            dt.downloader(furl(mod[1]), './download_confs/', f'{repo_name}.dconf', skip=True)
            
            with open(f'./download_confs/{repo_name}.dconf', 'r') as file:
                vconf = file.read().split('\n')[0]

                if vconf == 'git':
                    version = "1" # заглушка
                elif vconf[0] == 'v':
                    version = vconf[0]
                else:
                    vconf = 'url'
            
            if vconf == 'url':
                mod_loader = dt.download(f'./download_confs/{repo_name}.dconf', skip=False, out_data=True)
                version_path = next(mod_loader)[0]
                with open(version_path, 'r') as version_file:
                    version = version_file.read().split('\n')[0]

            if version > dmod_conf[repo_name]:
                print('need to update')

            else:
                print("normal")

    try:
        shutil.rmtree("./temp_files/")
    except Exception:
        pass


def __install(repo_name, compilation_branch, mod_branch, local_name=''):
    try:
        
        if not os.path.exists("./download_confs/local_name"):
            pass #dt.download()

        if not os.path.exists("./temp_files"):
            os.mkdir("./temp_files")

        

    except Exception as e:
        print("[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()
