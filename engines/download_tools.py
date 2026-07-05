import urllib.request
from math import floor

from sys import argv
import os
import zipfile


def download(file_url, file_path, file_name, skip=False):

    percent = 0
    
    with urllib.request.urlopen(file_url) as response:
        
        total_length = response.info().get('Content-Length')
        
        print(f"Installing {file_name}")
        total_length = int(total_length)
        
        if skip and os.path.exists(file_path + file_name) and os.path.getsize(file_path + file_name) == total_length:
            print("File exists, skipping.")
            return
        
        downloaded = 0

        headers = {}
        
        if skip and os.path.exists(file_path + file_name):
            downloaded = os.path.getsize(file_path + file_name)
            headers = {'Range': f'bytes={downloaded}-'}
        
        chunk_size = 8192

    req = urllib.request.Request(file_url, headers=headers)
    
    with urllib.request.urlopen(req) as response, open(file_path + file_name, 'ab') as out_file:
    
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
                print(f"\r[{"#" * floor(percent / 5)}{' ' * ((100 - percent) // 5)}] {percent}% ({total_length // 1048576} MB)   ", end='')
    
    print("\ninstalled.")


def unzip(file_url, file_path, temp_name, skip=False, file_names=[]):
    os.mkdir("./temp_files")
    download(file_url, "./tem_files", temp_name, skip=skip)

    if file_names != 0:
        for file_name in file_names:
            


if __name__ == "__main__":
    url = argv[1]
    file_path = argv[2]
    file_name = argv[3]
    skip = False
    print(argv[4])
    if argv[4] == "s":
        skip = True

    print(argv[4] == "s")
    
    download(url, file_path, file_name, skip)
