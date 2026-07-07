import shutil
import zipfile
import os

import download_tools as dt
from base_methods import *


def update(repo_name):
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    modlist = {}
    dt.downloader(furl('[RURL]index.modlist'), "./temp_files/", "modlist.txt", skip=False)
    with open("./temp_files/modlist.txt", 'r') as f:
        for x in modlist.split('\n'):
            mod = list(x.split(';'))

            if mod[0] == repo_name:
                dt.downloader(furl(mod[1]), )

    shutil.rmtree("./temp_files/")


def __install(repo_name, compilation_branch, mod_branch, local_name=''):
    try:
        
        if not os.path.exists("./download_confs/local_name"):
            dt.download()

        if not os.path.exists("./temp_files"):
            os.mkdir("./temp_files")

        

    except Exception as e:
        print("[error] not installed {repo_name}")
        print(f"[log] error: {e}")
        caption()



# def update_be():

#     if not os.path.exists("./temp_files"):
#         os.mkdir("./temp_files")
    
#     name = "zz-osp-pak8be.pk3"
#     be_url = "https://konstalker.github.io/assets/zz-osp-pak8be.pk3"
    
#     archive_path = '../baseq3/mods/osp/'
#     vurl = "https://konstalker.github.io/assets/version.txt"
#     vfile = 'version.txt'

#     dt.downloader(vurl, "./temp_files/", vfile)
#     download = False
    
#     try:
#         if not os.path.exists(archive_path + name):
#             download = True
        
#         if not download:
#             with zipfile.ZipFile(archive_path + name, 'r') as archive:
#                 with archive.open(vfile) as oldfile, open(f"./temp_files/{vfile}", 'r') as newfile:
#                     old = oldfile.read().decode('utf-8')
#                     new = newfile.read()
#                     if old < new:
#                         download = True
#                         os.remove(archive_path + name)

#         if download:
#             dt.downloader(be_url, archive_path, name, skip=True)
#         else:
#             print(f"[log] you have newest version of {name}")

#         shutil.rmtree("./temp_files/")
                
#     except Exception as e:
#         print("[error] new versoin of OSP2-BE not installed")
#         print(f"[log] error: {e}")
#         caption()


if __name__ == "__main__":
    print(furl("[RURL]index.modlist"))
