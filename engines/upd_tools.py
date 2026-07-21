import shutil
from sys import version, argv
import zipfile
import os
import json

import download_tools as dt
from base_methods import caption, furl, c_info

from dmods_tools import dmod_conf


def autoupdate():
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    dt.downloader(furl('[RURL]index.modlist'), "./temp_files/", "modlist.txt", skip=True)
   
    with open("./temp_files/modlist.txt", 'r') as f:
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

            print(modlist[repo_name])
            

    except Exception as e:
        print(f"[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()


if __name__ == "__main__":
    update(argv[1])
