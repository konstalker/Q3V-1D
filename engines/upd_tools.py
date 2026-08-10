import shutil
from sys import argv, version
import zipfile
import os
import json

import download_tools as dt
from base_methods import *

from bmods_tools import bmod_conf


def get_modlist():
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)

    if not os.path.exists('./temp_files/modlist.json'):
        return False
    with open('./temp_files/modlist.json', 'r', encoding='utf-8') as f:
        modlist = json.load(f)

    return modlist
    

def autoupdate(skip=False):
    updates = get_updates()

    for x in updates:
        update(x)


def get_version(repo_name):
    modlist = get_modlist()
    if not modlist:
        return 0
        
    version = modlist[repo_name]["version"]
    if (version[0] != 'v' and version[0] != 'git') and\
    check_url(modlist[repo_name]["version"]):
        dt.downloader(modlist[repo_name]["version"], './temp_files/', 'version.txt')

        with open('./temp_files/version.txt', 'r') as file:
            version = file.read().rstrip()
    elif version == 'git':
        version = '1'
    elif version[0] == 'v':
        pass
    return version

def get_updates():
    needed = []
    modlist = get_modlist()
    if not modlist:
        return []
    for repo_name in bmod_conf.mod_list():

        print(f'Check updates for {repo_name}')
        
        if repo_name not in modlist:
            print(f'{repo_name} not in modlist, skipping.')
            continue
        
        need_update = False
        version = get_version(repo_name)
        
        if bmod_conf[repo_name] < version:
            need_update = True

        if need_update:
            needed.append(repo_name)
            
            print(f'Old version: {bmod_conf[repo_name]}')
            print(f'New version: {version}')
            print('Update required.')
            
    return needed


def update(repo_name, repare=False):
    print(f'Updating {repo_name}...')
    try:
        modlist = get_modlist()
        
        if not modlist:
            return

        dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=repare)
        dt.download(f'./download_confs/{repo_name}.dconf', skip=repare)

        # bmod changes

        dl_mods = bmod_conf.mod_info[modlist[repo_name]["tag"]]
        for x in dl_mods[:-1]:
            _rm(x)
            bmod_conf[repo_name] = None, modlist[repo_name]['tag']

        version = get_version(repo_name)
        bmod_conf[repo_name] = version, modlist[repo_name]["tag"]
        bmod_conf.save()

    except Exception as e:
        print(f"[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()

def _rm(repo_name):
    dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)
    with open('./temp_files/modlist.json', 'r', encoding='utf-8') as f:
        modlist = json.load(f)

    assert repo_name in modlist, "mod not in modlist, cannot be removed."
    
    dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=True)
        
    with open(f'./download_confs/{repo_name}.dconf', 'r') as dconf_file:
        dconf = list(dconf_file.read().split('\n'))

    for x in dconf:

        # change for files
        x = list(x.split(';'))[4::2]

        for path in x:

            print('remove:', path)

            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
            except Exception:
                print('[warning] files not found.')
    
    bmod_conf[repo_name] = None, modlist[repo_name]["tag"]

def remove(repo_name):
    print(f'Removing {repo_name}...')

    try:
        _rm(repo_name)
        autoupdate(skip=True)
        bmod_conf.save()
        
    except Exception as e:
        print(f"[error] not removed {repo_name}")
        print(f"[log] error: {e}")


if __name__ == "__main__":
    update(argv[1])
