import shutil
from sys import argv, version
import zipfile
import os
import json
import urllib.request
import urllib.error

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


def get_git_hash(repo):
    """
    repo: репозиторий в формате 'owner/name' (GitHub).
    Возвращает хэш коммита последнего релиза, либо None при ошибке.
    """
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'upd_tools',
    }

    try:
        req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}/releases/latest',
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            release = json.load(resp)

        tag = release.get('tag_name')
        if not tag:
            print(f'[warning] no tag_name found for latest release of {repo}')
            return None

        req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}/commits/{tag}',
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            commit = json.load(resp)

        return commit.get('sha')

    except urllib.error.HTTPError as e:
        print(f'[error] GitHub API error for {repo}: {e}')
        return None
    except Exception as e:
        print(f'[error] failed to get git hash for {repo}: {e}')
        return None


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
        repo = modlist[repo_name].get('repo')
        if not repo:
            print(f'[warning] {repo_name}: version is "git", but no "repo" field in modlist (format "owner/name"), skipping hash lookup.')
            version = '1'
        else:
            git_hash = get_git_hash(repo)
            version = git_hash if git_hash else '1'
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

        if modlist[repo_name]["version"] == 'git':
            # хэш коммита нельзя сравнивать через "<" — сравниваем на несовпадение
            if bmod_conf[repo_name] != version:
                need_update = True
        elif bmod_conf[repo_name] < version:
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

def _is_protected_path(path):
    """Не даём снести общие/системные директории целиком."""
    abs_path = os.path.abspath(path)
    protected = {
        os.path.abspath('.'),               # сама папка engines — НИКОГДА не удаляем
        os.path.abspath('..'),              # корень репозитория
        os.path.abspath('../baseq3'),       # общая папка игры
        os.path.abspath('../baseq3/mods'),  # общая папка модов (родитель для всех модов)
    }
    return abs_path in protected


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
            entries = [(arr[1], arr[3])]      # (src_name, dest_dir)
        elif arr[0] == 'a':
            entries = list(zip(arr[3::2], arr[4::2]))
        else:
            continue

        for src, dest in entries:
            file_path = os.path.join(dest, os.path.basename(src))
            dir_path = dest.rstrip('/') or '.'

            # 1. Пробуем удалить как конкретный файл — это безопасно всегда
            try:
                if os.path.isfile(file_path):
                    print('remove file:', file_path)
                    os.remove(file_path)
                    continue
            except Exception as e:
                print(f'[warning] could not remove {file_path}: {e}')
                continue

            # 2. Фоллбэк на удаление целой папки — только если это НЕ общая/системная директория
            if _is_protected_path(dir_path):
                print(f'[warning] refusing to delete shared/system directory: {dir_path}')
                continue

            try:
                if os.path.isdir(dir_path):
                    print('remove dir:', dir_path)
                    shutil.rmtree(dir_path)
                else:
                    print(f'[warning] path not found: {file_path} / {dir_path}')
            except Exception as e:
                print(f'[warning] could not remove {dir_path}: {e}')

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
