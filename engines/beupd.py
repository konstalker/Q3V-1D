import shutil
import zipfile
import os

import download_tools as dt
from caption import caption


def update_be():

    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")
    
    name = "zz-osp-pak8be.pk3"
    be_url = "https://konstalker.github.io/assets/zz-osp-pak8be.pk3"
    
    archive_path = '../baseq3/mods/osp/'
    vurl = "https://konstalker.github.io/assets/version.txt"
    vfile = 'version.txt'

    dt.downloader(vurl, "./temp_files/", vfile)
    download = False
    
    try:
        if not os.path.exists(archive_path + name):
            download = True
        
        if not download:
            with zipfile.ZipFile(archive_path + name, 'r') as archive:
                with archive.open(vfile) as oldfile, open(f"./temp_files/{vfile}", 'r') as newfile:
                    old = oldfile.read().decode('utf-8')
                    new = newfile.read()
                    if old < new:
                        download = True
                        os.remove(archive_path + name)

        if download:
            dt.downloader(be_url, archive_path, name, skip=True)
        else:
            print(f"[log] you have newest version of {name}")

        shutil.rmtree("./temp_files/")
                
    except Exception as e:
        print("[error] new versoin of OSP2-BE not installed")
        print(f"[log] error: {e}")
        caption()


if __name__ == "__main__":
    update_be()