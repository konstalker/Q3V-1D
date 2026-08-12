import shutil
from sys import argv, version
import zipfile
import os
import json

import download_tools as dt
from base_methods import *

from bmods_tools import bmod_conf


def _create_paths(paths, files):
    
    paths = list(zip(paths, files))
    for i, x in enumerate(paths):
        paths[i] = x[0] + x[1][(x[1].rindex('/') + 1 if '/' in x[1] else 0):]

    return paths

def get_modlist():
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    dt.downloader(furl('[RURL]index.json'), "./temp_files/", "modlist.json", skip=True)

    if not os.path.exists('./temp_files/modlist.json'):
        return False
    else:
        with open('./temp_files/modlist.json', 'r', encoding='utf-8') as f:
            modlist = json.load(f)

    return modlist
    

def autoupdate(skip=False):
    updates = get_updates()
    
    for x in updates:
        update(x, repare=skip)


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

        dl_mods = bmod_conf.mod_info.get(modlist[repo_name]["tag"], [])
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
    modlist = get_modlist()
    if not modlist:
        raise FileNotFoundError(f"Cannot delete mod, modlist not found.")

    if repo_name not in modlist:
        raise KeyError(f"{repo_name} mod not in modlist, cannot be removed.")

    dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=True)
    if not os.path.exists(f'./download_confs/{repo_name}.dconf'):
        raise FileNotFoundError(f"Didn't installed dconf for {repo_name}, cannot be removed.")

    with open(f'./download_confs/{repo_name}.dconf', 'r') as dconf_file:
        dconf = dconf_file.read().split('\n')

    for line in dconf:
        if ';' not in line:
            continue

        arr = line.split(';')

        if arr[0] == 'f':
            targets = [os.path.join(arr[3], arr[1])]
        elif arr[0] == 'a':
            targets = []
            for src, dest in zip(arr[3::2], arr[4::2]):
                targets.append(os.path.join(dest, os.path.basename(src)))
                targets.append(dest.rstrip('/'))
        else:
            continue

        for path in targets:
            print('remove:', path)
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    if arr[0] == 'f':
                        break
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                print(f'[warning] could not remove {path}: {e}')

    bmod_conf[repo_name] = None, modlist[repo_name]["tag"]

def remove(repo_name):
    print(f'Removing {repo_name}...')

    try:
        _rm(repo_name)
        bmod_conf.save()          # фиксируем удаление сразу, не дожидаясь autoupdate
    except Exception as e:
        print(f"[error] not removed {repo_name}")
        print(f"[log] error: {e}")
        return

    try:
        autoupdate(skip=True)
        bmod_conf.save()
    except Exception as e:
        print(f"[warning] auto-update after removal failed: {e}")

if __name__ == "__main__":
    update(argv[1])
