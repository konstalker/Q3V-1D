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
    modlist = get_modlist()

    # Приоритет теперь (branch, index). Сортировка Python сравнивает tuple
    # поэлементно — сначала по имени ветки, затем по индексу внутри неё.
    # Порядок МЕЖДУ ветками тут произвольный (алфавит имени ветки), и это
    # нормально: раз ветки не пересекаются по файлам, порядок установки
    # между ними не влияет на результат. Важен только порядок ВНУТРИ
    # ветки — он соблюдается корректно.
    if modlist:
        updates.sort(key=lambda r: bmod_conf.priority_of_tag(modlist[r]['tag']) if r in modlist else ('~unknown', 999999))

    for x in updates:
        update(x, repare=skip)

    bmod_conf.check_priority_sanity()


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

    entry = modlist[repo_name]
    version_type = entry.get("version_type")
    version = entry.get("version")

    if version_type == "url":
        if not check_url(furl(version)):
            print(f'[warning] {repo_name}: version_type is "url", but "version" ({furl(version)}) is not a reachable url.')
            return furl(version)

        dt.downloader(version, './temp_files/', 'version.txt')

        with open('./temp_files/version.txt', 'r') as file:
            version = file.read().rstrip()

    elif version_type == "git":
        repo = version
        if not repo:
            print(f'[warning] {repo_name}: version_type is "git", but "version" (repo, format "owner/name") is not set, skipping hash lookup.')
            version = '1'
        else:
            git_hash = get_git_hash(repo)
            version = git_hash if git_hash else '1'

    elif version_type == "version":
        pass

    else:
        print(f'[warning] {repo_name}: unknown version_type "{version_type}", expected "version", "url" or "git".')

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

        if modlist[repo_name].get("version_type") == 'git':
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

        tag = modlist[repo_name]["tag"]

        # Если под этим тегом уже стоит ДРУГОЙ мод — сносим его перед установкой нового
        current = bmod_conf.mod_info.get(tag)
        if current and current[1] != '0' and current[0] != repo_name:
            print(f'{current[0]} occupies tag "{tag}", removing before installing {repo_name}...')
            _rm(current[0])

        dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=repare)
        installed_files = dt.download(f'./download_confs/{repo_name}.dconf', skip=repare)

        # Манифест — это то, что реально легло на диск сейчас, а не то,
        # что "должно было" по .dconf. При первой установке файла с
        # деревом ещё не было — он и появляется этой строкой.
        bmod_conf.save_manifest(repo_name, installed_files or [])

        version = get_version(repo_name)
        bmod_conf[repo_name] = version, tag
        bmod_conf.save()

        # repo_name мог физически перезаписать файлы, которыми уже владел
        # какой-то более приоритетный (по тегу) активный мод — например,
        # сборку скачали ПОСЛЕ уже установленного точечного аддона.
        # Порядок закачки в этом случае не важен: пересобираем поверх.
        _reapply_higher_priority(repo_name, tag, modlist)
        
        if repo_name == "scripts":
            if c_info.s_data == "windows":
                subprocess.Popen(["./python/setup_python.bat", "./launch.pyw"])
            else:
                os.system("chmod +x ./python/setup_python.sh")
                subprocess.Popen(["./python/setup_python.sh", "./launch.pyw", "upd"])
            sys.exit(0)

    except Exception as e:
        print(f"[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()


def _reapply_higher_priority(repo_name, tag, modlist):
    """После установки repo_name — переустановить поверх все активные моды
    с более высоким приоритетом ВНУТРИ ТОЙ ЖЕ ВЕТКИ tag_order.txt, чьи
    файлы реально пересекаются с только что установленными. Переустанавливаются
    ТОЛЬКО конкретные пересекающиеся файлы (wanted_paths), а не весь
    архив/мод целиком. Манифест затронутого мода при этом не трогаем.

    Если пересечение находится с модом из ДРУГОЙ ветки — по конфигурации
    это не должно происходить, поэтому вместо угадывания победителя
    печатается предупреждение и ничего не восстанавливается автоматически."""
    my_priority = bmod_conf.priority_of_tag(tag)
    my_files = set(bmod_conf.load_manifest(repo_name))
    if not my_files:
        return

    for other_tag, (other_repo, _version) in list(bmod_conf.mod_info.items()):
        if other_repo == repo_name:
            continue

        other_priority = bmod_conf.priority_of_tag(other_tag)
        other_files = set(bmod_conf.load_manifest(other_repo))
        overlap = my_files & other_files
        if not overlap:
            continue

        if other_priority[0] != my_priority[0]:
            print(f'[warning] {other_repo} (ветка {other_priority[0]}) неожиданно делит '
                  f'{len(overlap)} файлов с {repo_name} (ветка {my_priority[0]}) — ветки не '
                  f'связаны в tag_order.txt, авто-восстановление пропускаю, проверьте конфиг')
            continue

        if other_priority[1] <= my_priority[1]:
            continue

        print(f'[reconcile] {other_repo} (приоритет {other_priority[1]} в ветке {other_priority[0]}) '
              f'пересекается с {repo_name} по {len(overlap)} файлам — восстанавливаю только их')
        try:
            dt.download(f'./download_confs/{other_repo}.dconf', skip=True, wanted_paths=overlap)
        except Exception as e:
            print(f'[warning] не удалось восстановить файлы {other_repo} поверх {repo_name}: {e}')

def _is_protected_path(path):
    """Не даём снести общие/системные директории целиком."""
    abs_path = os.path.abspath(path)
    protected = {
        os.path.abspath('.'),
        os.path.abspath('..'),
        os.path.abspath('../baseq3'),
        os.path.abspath('../baseq3/mods'),
        os.path.abspath('../baseq3/mods/osp'),
    }
    return abs_path in protected


def _rm(repo_name):
    """Удаляет мод по его манифесту (bmod_conf.load_manifest): точный список
    того, что реально было положено на диск при установке, а не
    реконструкция по (возможно уже изменившемуся) .dconf.

    Файл удаляется, только если он до сих пор реально принадлежит этому
    мода (build_ownership) — если его уже перекрыл более приоритетный
    мод, трогать его нельзя: он больше не "наш".

    Для модов, установленных ДО этого патча (манифеста ещё нет) —
    фоллбэк на старый способ через парсинг .dconf, чтобы не оставлять
    файлы-сироты на диске молча.
    """
    modlist = get_modlist()
    if not modlist:
        raise FileNotFoundError(f"Cannot delete mod, modlist not found.")

    if repo_name not in modlist:
        raise KeyError(f"{repo_name} mod not in modlist, cannot be removed.")

    if not bmod_conf.has_manifest(repo_name):
        print(f'[info] нет манифеста для {repo_name} (стоял до этого патча) — '
              f'удаляю по старой схеме через .dconf')
        _rm_legacy(repo_name, modlist)
        bmod_conf[repo_name] = None, modlist[repo_name]["tag"]
        return

    owners = bmod_conf.build_ownership()

    for path in bmod_conf.load_manifest(repo_name):
        owner = owners.get(path)
        if owner and owner[0] != repo_name:
            print(f'[skip] {path}: сейчас реально принадлежит {owner[0]}, не трогаю')
            continue
        try:
            if os.path.isfile(path):
                print('remove file:', path)
                os.remove(path)
        except Exception as e:
            print(f'[warning] could not remove {path}: {e}')

    bmod_conf.delete_manifest(repo_name)
    bmod_conf[repo_name] = None, modlist[repo_name]["tag"]


def _rm_legacy(repo_name, modlist):
    """Старая логика удаления через разбор .dconf — только как фоллбэк
    для модов без манифеста (см. _rm)."""
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


def remove(repo_name):
    print(f'Removing {repo_name}...')

    try:
        _rm(repo_name)
        bmod_conf.save()
    except Exception as e:
        print(f"[error] not removed {repo_name}")
        print(f"[log] error: {e}")

    try:
        autoupdate(skip=True)
        bmod_conf.save()
    except Exception as e:
        print(f"[warning] auto-update after removal failed: {e}")

if __name__ == "__main__":
    update(argv[1])
