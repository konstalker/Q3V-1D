import shutil
import time
import urllib.request
from math import floor
from base_methods import *

from sys import argv
import os
import zipfile
from shutil import rmtree


def downloader(file_url, file_path, file_name, skip=False, attempt=0, max_attempts=10):

    if attempt == max_attempts:
         print(f"{file_name} not downloaded.")
         return []

    try:
        percent = 0
        chunk_size = 16384
        
        with urllib.request.urlopen(file_url, timeout=4) as response:
            
            total_length = response.info().get('Content-Length')
            
            print(f"Installing {file_name}")
    
            if total_length != None:
                total_length = int(total_length)
            else:
                total_length = chunk_size
                print(file_url, 'has no length data')
            
            if skip and os.path.exists(file_path + file_name) and os.path.getsize(file_path + file_name) == total_length:
                print("File exists, skipping.")
                return [file_path + file_name]
            
            downloaded = 0
    
            headers = {}
            
            if skip and os.path.exists(file_path + file_name):
                downloaded = os.path.getsize(file_path + file_name)
                headers = {'Range': f'bytes={downloaded}-'}
        
        req = urllib.request.Request(file_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=4) as response, open(file_path + file_name, 'ab' if skip else 'wb') as out_file:
    
            print("downloading...")
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break 
                
                out_file.write(chunk)
                downloaded += len(chunk)
                
                # 3. Высчитываем проценты и обновляем строку в консоли
                last_percent = percent
                percent = int((downloaded / total_length) * 100)
    
                if last_percent != percent:
                    print(f"\r[{'#' * floor(percent / 5)}{' ' * floor((100 - percent) // 5)}] {percent}% ({total_length // 1048576} MB)   ", end='')
        
        if downloaded == total_length:
            print("\ninstalled.")
            return file_path + file_name

    except Exception:
        time.sleep(2)
        downloader(file_url, file_path, file_name, attempt=attempt + 1, max_attempts=max_attempts)


def unziper(file_url, name, file_paths=[], skip=False):

    installed = []

    if os.path.exists("./temp_files/" + name) and not skip:
        os.remove("./temp_files/" + name)
    
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")
    downloader(file_url, "./temp_files/", name, skip=True)

    with zipfile.ZipFile(f"./temp_files/{name}", 'r') as zip_ref:
        zip_ref.extractall(f"./temp_files/{name}dir")
    
    for file_path in file_paths:
        temp_name = furl(f"./temp_files/{name}dir/{file_path[0]}")
        
        assert os.path.exists(temp_name), f"no such file or directory: {temp_name}"

        if os.path.isfile(temp_name):
            print(temp_name)
            shutil.copy(temp_name, file_path[1])
            installed.append(temp_name)
        else:
            if os.path.exists(temp_name) and os.path.exists(file_path[1]):
                shutil.rmtree(temp_name, file_path[1])
            shutil.copytree(temp_name, file_path[1])
            installed.extend(get_relative_paths(file_path[1]))
    try:
        rmtree("./temp_files")
    except Exception:
        pass

    return installed



def download(conf_file, skip=False):

    arr = [None]
    
    try:
    
        with open(conf_file, 'r') as pack_file:
            pack_list = pack_file.read().split('\n')
            
            for (i, _) in enumerate(pack_list):
                installed = []
                
                if ';' in _:
                    arr = _.split(';')

                    if arr[0] == "a":
                        
                        files = []
                        url, name = arr[2], arr[1]
                        
                        for start, end in zip(arr[3::2], arr[4::2]):
                            files.append([start, end])

                        unziper(furl(url), name, files, skip=skip)
                        
                    elif arr[0] == 'f':

                        installed.append(downloader(furl(arr[2]), arr[3], arr[1], skip=skip))

                    else:

                        raise TypeError (f"uncorrect datatype: {arr[0]} in {arr[1]}")

                yield installed

    except Exception as err:
        print(f'[log] {err}')
        print(f"[error] not installed {arr[1]}")
        input()
        if arr[0] == 'a':
            rmtree(f"./temp_files/{arr[1]}dir", )
        caption()


if __name__ == "__main__":
    download_conf = argv[1]
    if len(argv) >= 3 and argv[2] == "skip":
        s = True
    else:
        s = False
        
    list(download(download_conf, skip=s))
