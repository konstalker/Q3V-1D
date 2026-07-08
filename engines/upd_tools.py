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
            
            dt.downloader(furl(mod[1]), './temp_files/', f'{repo_name}.dconf', skip=True)
            mod_loader = dt.download(f'./temp_files/{repo_name}.dconf', skip=False, out_data=True)
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
    update("osp2-be")
    update("oDFe")
