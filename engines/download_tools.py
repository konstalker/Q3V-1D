from ast import Delete
import urllib.request
from multiprocessing import Process
from sys import argv
import os
from math import floor
import time

def __download_proc(file_url, file_path, skip, index, processes, total_length, chunk_size):

    downloaded = index * (total_length // processes) + os.path.getsize(file_path + file_name + f'.part{index}')
    if processes - 1 == index:
        partend = ''
    else:
        partend = (index + 1) * floor(total_length / processes)
    
    headers = {'Range': f'bytes={downloaded}-{partend}'}
    req = urllib.request.Request(file_url, headers=headers)

    with urllib.request.urlopen(req) as response, open(file_path + file_name + f'.part{index}', 'ab') as out_file:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break 
            
            out_file.write(chunk)
    

def download(file_url, file_path, file_name, skip=False, processes=1, chunk_size=8192):
    with urllib.request.urlopen(file_url) as response:
        
        total_length = response.info().get('Content-Length')
        total_length = int(total_length)
        
        print(f"Installing {file_name}")
        
        if skip and os.path.exists(file_path + file_name) and os.path.getsize(file_path + file_name) == total_length:
            print("File exists, skipping.")
            return

        downloaders = []
        downloaded = 0

        last_percent = 0
        percent = 0
        
        for i in range(processes):
            downloaders.append(Process(target=__download_proc, args=(file_url, file_path, skip, i, processes, total_length, chunk_size)))
            downloaders[i].start()

        while all([downloaders[i].is_alive() for i in range(processes)]):
            for i in range(processes):
                if os.path.exists(file_path + file_name + f'.part{i}'):
                    downloaded += os.path.getsize(file_path + file_name + f'.part{i}')
                    
            last_percent = percent
            percent = int((downloaded / total_length) * 100)
            if last_percent != percent:
                print(f"\r[{"#" * floor(percent / 5)}{' ' * ((100 - percent) // 5)}] {percent}% ({total_length // 1048576} MB)   ", end='')
            time.sleep(0.5)

        Delete(downloaders)

    with open(file_path + file_name, 'wb') as out_file:
        for i in range(processes):
            with open(file_path + file_name + f".part{i}", 'rb') as in_file:
                out_file.write(in_file.read())
            
            os.remove(file_path + file_name + f".part{i}")
    
    print("\ninstalled")

        
    
    '''with urllib.request.urlopen(req) as response, open(file_path + file_name, 'ab') as out_file:
    
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
                print(f"\r[{"#" * floor(percent / 5)}{' ' * ((100 - percent) // 5)}] {percent}% ({total_length // 1048576} MB)   ", end='')'''
    
    print("\ninstalled.")



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
