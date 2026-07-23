import shutil
from sys import version, argv
import zipfile
import os
import json

import download_tools as dt
from base_methods import *

from dmods_tools import dmod_conf


def autoupdate():
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)
   
    with open("./temp_files/modlist.json", 'r') as f:
        for x in dmod_conf.mod_list():
            update(x)

    dmod_conf.save()

    try:
        shutil.rmtree("./temp_files/")
    except Exception:
        pass


def update(repo_name):
    try:
        if not os.path.exists("./temp_files"):
            os.mkdir("./temp_files")
    
        dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)
        with open('./temp_files/modlist.json', 'r', encoding='utf-8') as f:
            modlist = json.load(f)

        need_update = False

        version = modlist[repo_name]["version"]        
        if (version[0] != 'v' or version[0] != 'git') and\
           check_url(modlist[repo_name]["version"]):
            dt.downloader(modlist[repo_name]["version"], './temp_files/', 'version.txt')

            with open('./temp_files/version.txt', 'r') as file:
                version = file.read().rstrip()
        
        if dmod_conf[repo_name] == '0':
            need_update = True

        else:

            if version == 'git':
                version = 1 # need to check hash
                if dmod_conf[repo_name] != version:
                    need_update = True
            
            elif version[0] == 'v':
                if dmod_conf[repo_name] < version:
                   need_update = True
            
            else:
                if check_url(version):

                    with open('version.txt', 'r') as file:
                        version = file.read().rstrip()
                    
                    if version > dmod_conf[repo_name]:
                        need_update = True

                else:
                    raise ValueError(f'Unknown version type: {modlist[repo_name]["version"]}')
                
        print(f'Old version: {dmod_conf[repo_name]}')
        print(f'New version: {version}')
        print('Update required.' if need_update else 'Last version installed.')

        if need_update:
            dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=True)
            dt.download(f'./download_confs/{repo_name}.dconf', skip=False)
            dmod_conf[repo_name] = version

    except Exception as e:
        print(f"[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()


if __name__ == "__main__":
    update(argv[1])
