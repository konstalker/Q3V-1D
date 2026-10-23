import shutil
from sys import argv, version
import zipfile
import os
import json
import urllib.request
import urllib.error
import time

from shutil import rmtree

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


# Global list of all mod names (repo names/keys) in bmod_conf.mod_info
# Used by _rm to find overlapping mods during deletion. Updated on load.
# Initialized lazily when first accessed to ensure it's fresh
_all_mods = None

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
    """Get the SHA hash of the latest release for a GitHub repo."""
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
            print('[warning] no tag_name found for latest release of {}', repo)
            return None

        req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}/commits/{tag}',
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            commit = json.load(resp)

        return commit.get('sha')

    except urllib.error.HTTPError as e:
        print('[error] GitHub API error for {}: {}'.format(repo, e))
        return None
    except Exception as e:
        print('[error] failed to get git hash for {}: {}'.format(repo, e), file=__import__('sys').stderr)
        return None


def get_version(repo_name):
    """Get the version string for a repo."""
    modlist = get_modlist()
    if not modlist:
        return "0"  # Always string

    entry = modlist[repo_name]
    version_type = entry.get("version_type")
    version = entry.get("version")

    if version_type == "url":
        if not check_url(furl(version)):
            print('[warning] {}: version_type is "url", but "version" ({}) is not reachable'.format(repo_name, furl(version)))
            version = str(furl(version))  # Always string
            return str(version)

        dt.downloader(version, './temp_files/', 'version.txt')

        with open('./temp_files/version.txt', 'r') as file:
            version = str(file.read().rstrip())  # Always string

    elif version_type == "git":
        repo = version
        if not repo:
            print('[warning] {}: version_type is "git", but "version" ({}) is missing'.format(repo_name, repo))
            version = '1'
        else:
            git_hash = get_git_hash(repo)
            if git_hash:
                version = str(git_hash)  # hash is string
            else:
                version = '0'  # fallback as string

    elif version_type == "version":
        pass

    else:
        print('[warning] {}: unknown version_type "{}"'.format(repo_name, version_type))

    return str(version) if version is not None else '0'  # Всегда строка

def get_updates():
    """Return a list of mods that need updating."""
    needed = []
    modlist = get_modlist()
    if not modlist:
        return []
    for repo_name in bmod_conf.mod_list():

        print('[info] Checking updates for {}...'.format(repo_name))
        
        if repo_name not in modlist:
            print('[skip] {} not in modlist, skipping.'.format(repo_name))
            continue
        
        need_update = False
        version = get_version(repo_name)

        if modlist[repo_name].get("version_type") == 'git':
            # Git hashes cannot be compared with ";" — compare for inequality
            if bmod_conf[repo_name] != version:
                need_update = True
        elif str(bmod_conf[repo_name]) < str(version):
            need_update = True

        if need_update:
            needed.append(repo_name)
            
            print('[info] {} requires update'.format(repo_name))
            print('[debug] Old version: {}'.format(bmod_conf[repo_name]))
            print('[debug] New version: {}'.format(version))
            
    return needed

def update(repo_name, repare=False):
    """Install/update a mod."""
    print('[info] Updating {}'.format(repo_name))
    try:
        modlist = get_modlist()
        if not modlist:
            return

        tag = modlist[repo_name]["tag"]

        # If another mod occupies this tag — remove it before installing the new one
        current = bmod_conf.mod_info.get(tag)
        if current and current[1] != '0' and current[0] != repo_name:
            print('[reconcile] {} occupies tag "{}"; removing before installing {}'.format(current[0], tag, repo_name))
            _rm(current[0])

        dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=repare)
        installed_files = dt.download(f'./download_confs/{repo_name}.dconf', skip=repare)

        # Manifest is what actually landed on disk now, not what "should have"
        # been according to .dconf. On first install, the file tree didn't exist
        # - it's created with this statement.
        bmod_conf.save_manifest(repo_name, installed_files or [])

        version = get_version(repo_name)
        bmod_conf[repo_name] = version, tag
        bmod_conf.save()

        # repo_name could have physically overwritten files that another mod
        # with higher priority (by tag) in the same branch already owned.
        # For example: you downloaded a patch AFTER installing a focused addon.
        # In this case, download order doesn't matter - we reapply on top.
        _reapply_higher_priority(repo_name, tag, modlist)
        
        if repo_name == "scripts":
            if c_info.s_data == "windows":
                subprocess.Popen(["./python/setup_python.bat", "./launch.pyw"])
            else:
                os.system("chmod +x ./python/setup_python.sh")
                subprocess.Popen(["./python/setup_python.sh", "./launch.pyw", "upd"])
            sys.exit(0)

    except Exception as e:
        print('[error] installation failed: {}'.format(e))
        caption()


def _reapply_higher_priority(repo_name, tag, modlist):
    """After installing repo_name — reapply all higher-priority mods
    from the same tag branch that overlap with the newly installed files.
    Only reinstating overlapping files (wanted_paths), not the entire archive/mod.
    Do not touch the manifest of the affected mod."""
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
            print('[warning] {} (branch {}) unexpectedly shares {} files with {} '
                  ' - branches are not linked in tag_order.txt, skipping auto-restore, check config'.format(
                other_repo, other_priority[0], len(overlap), repo_name, my_priority[0]))
            continue

        if other_priority[1] <= my_priority[1]:
            continue

        print('[reconcile] {} (priority {} in branch {}) overlaps with {} '
              f'by {len(overlap)} files - restoring only overlapping ones'.format(
                other_repo, other_priority[1], other_priority[0], repo_name))
        print('[debug] {} intersects with {}'.format(other_repo, repo_name))

def _is_protected_path(path):
    """Do not allow deleting common/system directories entirely."""
    abs_path = os.path.abspath(path)
    protected = {
        os.path.abspath('.'),
        os.path.abspath('..'),
        os.path.abspath('../baseq3'),
        os.path.abspath('../baseq3/mods'),
        os.path.abspath('../baseq3/mods/osp'),
    }
    return abs_path in protected


def _rm_legacy(repo_name, modlist):
    """Legacy removal logic via .dconf parsing - only as fallback
    for mods without manifest (see _rm)."""
    dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=True)
    if not os.path.exists(f'./download_confs/{repo_name}.dconf'):
        raise FileNotFoundError(f"Did not install dconf for {repo_name}, cannot be removed.")

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

            # Try removing as specific file - always safe
            try:
                if os.path.isfile(file_path):
                    print('[remove] Deleting {}'.format(file_path))
                    os.remove(file_path)
                    continue
            except Exception as e:
                print('[warning] Failed to remove {}: {}'.format(file_path, e))
                continue

            # Fallback to deleting entire directory - only if NOT common/system directory
            if _is_protected_path(dir_path):
                print('[warning] Refusing to delete shared/system directory: {}'.format(dir_path))
                continue

            try:
                if os.path.isdir(dir_path):
                    print('[remove] Deleting directory: {}'.format(dir_path))
                    shutil.rmtree(dir_path)
                else:
                    print('[warning] Path not found: {} or {}'.format(file_path, dir_path))
            except Exception as e:
                print(f'[warning] could not remove {dir_path}: {e}')

def _rm(repo_name):
    """Remove a mod by its manifest (bmod_conf.load_manifest): exact list
    of what was actually written to disk during installation, not a
    reconstruction from (possibly changed) .dconf."""
    modlist = get_modlist()
    if not modlist:
        raise FileNotFoundError("Cannot delete mod; modlist not found.")

    if repo_name not in modlist:
        raise KeyError("{} mod not in modlist, cannot be removed.".format(repo_name))

    # Get the tag of the current mod
    tag = modlist[repo_name]["tag"]
    
    # Global list of all mod names (repo names/keys) in bmod_conf.mod_info
    _all_mods = list(bmod_conf.mod_info.keys())
    
    if not bmod_conf.has_manifest(repo_name):
        print('[info] no manifest for {} (installed before this patch)'.format(repo_name))
        _rm_legacy(repo_name, modlist)
        bmod_conf[repo_name] = (None, tag)
        return

    # Determine priority of current mod: (branch, index)
    priority = bmod_conf.priority_of_tag(tag)
    
    current_branch, current_idx = priority
    
    # Find all mods that have the same files we're removing
    # These are the mods we need to check for restoration
    
    # Check if any mod has the same files we're removing
    # Use set operations - intersection returns empty set if no overlap
    has_overlap = False
    for t in _all_mods:
        t_paths = set(bmod_conf.load_manifest(t))
        current_paths = set(bmod_conf.load_manifest(repo_name))
        if t_paths & current_paths:  # Using & operator for set intersection
            has_overlap = True
            break
    
    has_lower_in_same_branch = False
    overlapping_mods = []
    
    if has_overlap:
        for t in _all_mods:
            t_paths = set(bmod_conf.load_manifest(t))
            current_paths = set(bmod_conf.load_manifest(repo_name))
            if t_paths & current_paths:
                overlapping_mods.append(t)
                # Check if any has lower priority
                if bmod_conf.priority_of_tag(t)[1] < current_idx:
                    has_lower_in_same_branch = True
    
    # Check priorities in same branch to determine if we are "high-priority" mod (restore type)
    # High-priority = our files overlap with files of lower mods (we restore them when removed)
    if has_overlap:
        overlapping_indices = [bmod_conf.priority_of_tag(t)[1] for t in overlapping_mods]
        is_high_priority = current_idx >= max(overlapping_indices)  # we are high-priority mod (restore)
    else:
        is_high_priority = True  # no overlapping mods - remove everything (no restoration needed)
    
    # Check if there are lower mods to restore from
    lower_mods = []
    if is_high_priority and overlapping_mods:
        lower_mods = [t for t in overlapping_mods if bmod_conf.priority_of_tag(t)[1] < current_idx]
    
    if is_high_priority:
        print('[delete] Removing HIGH-PRIORITY mod {} (tag {}, priority {}) - restoring files from lower-priority mods'.format(repo_name, tag, priority))
        
        # First restore files from lower-priority mods
        if lower_mods:
            for lower_tag in lower_mods:
                lower_paths = set(bmod_conf.load_manifest(lower_tag))
                current_paths = set(bmod_conf.load_manifest(repo_name))
                common = lower_paths & current_paths  # set intersection
                for p in common:
                    # Restore file from temporary archive of lower-priority mod
                    # temp_files/{lower_mod_name}/{filename}
                    lower_dir = os.path.join('.', 'temp_files', lower_tag)
                    temp_file = os.path.join(lower_dir, p)
                    if os.path.exists(temp_file):
                        print('[restore] Restoring {} from {} (lower mod: {})'.format(p, temp_file, lower_tag))
                        shutil.copy2(temp_file, p)
        
        # Remove files of this mod with retry logic
        for attempt in range(3):
            removed_all = True
            for path in bmod_conf.load_manifest(repo_name):
                abs_path = os.path.abspath(path).replace('\\', '/')
                try:
                    if os.path.isfile(abs_path):
                        print('[remove] Removing {} (attempt {}/3)'.format(abs_path, attempt + 1))
                        os.remove(abs_path)
                        removed_all = False
                    else:
                        removed_all = False
                except OSError as e:
                    # File may still exist from previous deletion attempt
                    print(f'[warning] Removal attempt {attempt + 1}/3 failed to remove {abs_path}: {e}. Retrying...')
                    # Wait and retry
                    time.sleep(0.3)
                    if os.path.isfile(abs_path):
                        print('[remove] Removal attempt {}/3 for {}'.format(attempt + 1, abs_path))
                        os.remove(abs_path)
                        removed_all = False
            
            if removed_all or attempt == 2:
                break
        
        # Clean up manifest and mod_info entries
        bmod_conf.delete_manifest(repo_name)
    if not is_high_priority:
        # 2. If we are LOWER index mod (core/low) -> block upper mods
        print('[info] Blocking removal of {} ({}, tag {}, priority {})'.format(
            repo_name, repo_name, tag, priority))
        print('[block] Files from higher-indexed mods protected against deletion')
        
        # Find paths that belong to HIGHER mods (in the same branch) - these are protected
        protected_paths = set()
        overlapping_mods_in_branch = [t for t in overlapping_mods
                                     if bmod_conf.priority_of_tag(t)[1] > current_idx]
        
        for higher_tag in overlapping_mods_in_branch:
            higher_paths = set(bmod_conf.load_manifest(higher_tag))
            current_paths = set(bmod_conf.load_manifest(repo_name))
            common = higher_paths & current_paths  # set intersection
            protected_paths.update(common)
        
        # Remove files that DO NOT belong to higher mods (i.e., our own or below us)
        for path in bmod_conf.load_manifest(repo_name):
            abs_path = os.path.abspath(path).replace('\\', '/')
            try:
                if os.path.isfile(abs_path):
                    # Check if this file is protected by a higher mod
                    if abs_path not in protected_paths:
                        print('[remove] Removing {} (owned by this mod or below)'.format(abs_path))
                        os.remove(abs_path)
                    else:
                        print('[block] File {} is protected by higher mod {}'.format(
                            abs_path, list(overlapping_mods_in_branch)[0] if overlapping_mods_in_branch else 'unknown'))
            except OSError as e:
                # First attempt failed - retry with small delay
                time.sleep(0.5)
                if os.path.isfile(abs_path):
                    print('[remove] Retrying removal of {}'.format(abs_path))
                    try:
                        os.remove(abs_path)
                    except OSError as e2:
                        print(f'[warning] Could not remove {abs_path} even on retry: {e2}')
        # Clean up manifest and mod_info entries
        bmod_conf.delete_manifest(repo_name)
    
    # Legacy removal logic via .dconf parsing - only as fallback
    # for mods without manifest (see _rm).
    dt.downloader(modlist[repo_name]["link"], './download_confs/', f'{repo_name}.dconf', skip=True)
    if not os.path.exists(f'./download_confs/{repo_name}.dconf'):
        raise FileNotFoundError(f"Did not install dconf for {repo_name}, cannot be removed.")

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

            # Try removing as specific file - always safe
            try:
                if os.path.isfile(file_path):
                    print('[remove] Deleting {}'.format(file_path))
                    os.remove(file_path)
                    continue
            except Exception as e:
                print('[warning] Failed to remove {}: {}'.format(file_path, e))
                continue

            # 2. Fallback to deleting entire directory - only if NOT common/system directory
            if _is_protected_path(dir_path):
                print('[warning] Refusing to delete shared/system directory: {}'.format(dir_path))
                continue

            try:
                if os.path.isdir(dir_path):
                    print('[remove] Deleting directory: {}'.format(dir_path))
                    shutil.rmtree(dir_path)
                else:
                    print('[warning] Path not found: {} or {}'.format(file_path, dir_path))
            except Exception as e:
                print(f'[warning] could not remove {dir_path}: {e}')


def remove(repo_name):
    """Remove a mod and auto-update."""
    print('[info] Removing {}'.format(repo_name))

    try:
        _rm(repo_name)
        bmod_conf.save()
    except Exception as e:
        print('[error] removal failed: {}'.format(e))

if __name__ == "__main__":
    update(argv[1])
