import shutil
from sys import version, argv
import zipfile
import os
import json

import download_tools as dt
from base_methods import *

from bmods_tools import bmod_conf


def autoupdate(skip=False):
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)
   
    with open("./temp_files/modlist.json", 'r') as f:
        for x in bmod_conf.mod_list():
            update(x, skip=skip)

    try:
        shutil.rmtree("./temp_files/")
    except Exception:
        pass


def update(repo_name, skip=False):
    print(f'Updating {repo_name}...')
    try:
        if not os.path.exists("./temp_files"):
            os.mkdir("./temp_files")
    
        dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)
        with open('./temp_files/modlist.json', 'r', encoding='utf-8') as f:
            modlist = json.load(f)

        if repo_name not in modlist:
            print(f'{repo_name} not in modlist, skipping.')
            return
        
        need_update = False
        
        version = modlist[repo_name]["version"]        
        if (version[0] != 'v' or version[0] != 'git') and\
           check_url(modlist[repo_name]["version"]):
            dt.downloader(modlist[repo_name]["version"], './temp_files/', 'version.txt')

            with open('./temp_files/version.txt', 'r') as file:
                version = file.read().rstrip()
        
        if bmod_conf[repo_name] == '0':

            if version == 'git':
                version = '1'
            need_update = True

        else:

            if version == 'git':
                version = "1" # need to check hash
                if bmod_conf[repo_name] != version:
                    need_update = True
            
            elif version[0] == 'v':
                if bmod_conf[repo_name] < version:
                   need_update = True
            
            else:
                with open('./temp_files/version.txt', 'r') as file:
                    version = file.read().rstrip()
                
                if version > bmod_conf[repo_name]:
                    need_update = True
                
        print(f'Old version: {bmod_conf[repo_name]}')
        print(f'New version: {version}')
        print('Update required.' if need_update else 'Last version installed.')

        if need_update:
            dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=skip)
            list(dt.download(f'./download_confs/{repo_name}.dconf', skip=skip))
            
            bmod_conf[repo_name] = version
            bmod_conf.save()

    except Exception as e:
        print(f"[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()


def remove(repo_name):
    print(f'Removing {repo_name}...')

    try:
        
        if not os.path.exists(f'./download_confs/{repo_name}.dconf'):
            dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)
            with open('./temp_files/modlist.json', 'r', encoding='utf-8') as f:
                modlist = json.load(f)
    
            assert repo_name not in modlist, "mod not in modlist, cannot be removed."

            dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=True)
            
        with open(f'./download_confs/{repo_name}.dconf', 'r') as dconf_file:
            dconf = list(dconf_file.read().split('\n'))

        for x in dconf:
            x = list(x.split(';'))[4::2]

            for path in x:

                print('remove:', path)
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                    
        bmod_conf[repo_name] = None
        autoupdate(skip=True)
        
    except Exception as e:
        print(f"[error] not removed {repo_name}")
        print(f"[log] error: {e}")


if __name__ == "__main__":
    update(argv[1])
