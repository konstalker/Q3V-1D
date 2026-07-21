import shutil
from base_methods import *

from sys import argv
import zipfile
from shutil import rmtree

import os
import time
import urllib.request
import urllib.error
import http.client
from math import floor


def downloader(file_url, file_path, file_name, skip=False, max_attempts=100):
    full_path = os.path.join(file_path, file_name)
    os.makedirs(file_path, exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    attempt = 0
    chunk_size = 16384

    while attempt < max_attempts:
        try:
            total_length = None
            
            # 1. Быстро узнаем размер файла через HEAD-запрос (без скачивания тела)
            try:
                head_req = urllib.request.Request(file_url, headers=headers, method='HEAD')
                with urllib.request.urlopen(head_req, timeout=9) as resp:
                    total_length = resp.info().get('Content-Length')
                    if total_length is not None:
                        total_length = int(total_length)
            except Exception:
                # Если сервер не поддерживает HEAD-запросы, обработаем это позже в GET
                pass

            # 2. Проверяем, скачан ли уже файл полностью
            if skip and total_length and os.path.exists(full_path):
                if os.path.getsize(full_path) == total_length:
                    print(f"\nFile {file_name} already exists and is complete. Skipping.")
                    return full_path

            # 3. Настраиваем докачку (Range Request)
            downloaded = 0
            write_mode = 'wb'
            req_headers = headers.copy()
            
            if skip and os.path.exists(full_path):
                downloaded = os.path.getsize(full_path)
                if downloaded > 0:
                    req_headers['Range'] = f'bytes={downloaded}-'
                    write_mode = 'ab'

            req = urllib.request.Request(file_url, headers=req_headers)
            
            # 4. Основной запрос на получение данных
            with urllib.request.urlopen(req, timeout=9) as response:
                status = response.getcode()
                
                # Защита от повреждения: если сервер проигнорировал Range и вернул 200 вместо 206,
                # значит докачка не поддерживается. Сбрасываем запись на начало файла ('wb')
                if write_mode == 'ab' and status != 206:
                    write_mode = 'wb'
                    downloaded = 0
                
                # Если не получили размер из HEAD, берем из текущего ответа
                if total_length is None or status == 206:
                    content_len = response.info().get('Content-Length')
                    if content_len is not None:
                        total_length = downloaded + int(content_len) if status == 206 else int(content_len)

                # Если размер так и остался неизвестным, ставим заглушку
                if total_length is None or total_length <= 0:
                    total_length = chunk_size

                print(f"Installing {file_name}...")
                percent = 0
                
                with open(full_path, write_mode) as out_file:
                    while True:
                        try:
                            # Читаем данные чанками
                            chunk = response.read(chunk_size)
                        except http.client.IncompleteRead as e:
                            # Важно: если связь оборвалась на полуслове, спасаем то, что успело прийти
                            chunk = e.partial
                        
                        if not chunk:
                            break
                            
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Вывод прогресс-бара
                        if total_length > 0:
                            last_percent = percent
                            percent = int((downloaded / total_length) * 100)
                            if last_percent != percent:
                                mb_total = total_length // 1048576
                                bar = '#' * floor(percent / 5)
                                spaces = ' ' * floor((100 - percent) // 5)
                                print(f"\r[{bar}{spaces}] {percent}% ({mb_total} MB)   ", end='', flush=True)

                # Проверяем целостность скачанного файла по размеру
                if downloaded >= total_length:
                    print("\nInstalled successfully.")
                    return full_path
                else:
                    raise Exception("Connection closed prematurely (size mismatch).")

        except (urllib.error.URLError, ConnectionError, TimeoutError, http.client.HTTPException, OSError) as e:
            attempt += 1
            print(f'\nNetwork issue: {e}. Retrying ({attempt}/{max_attempts})...')
            time.sleep(1)

    print(f"\nFailed to download {file_name} after {max_attempts} attempts.")
    return None


def unziper(file_url, name, file_paths=[], skip=False):

    installed = []

    if os.path.exists("./temp_files/" + name) and not skip:
        os.remove("./temp_files/" + name)
    
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")
    
    if not os.path.exists("./cache"):
        os.mkdir("./cache")

    downloader(file_url, "./cache/", name, skip=True)

    with zipfile.ZipFile(f"./cache/{name}", 'r') as zip_ref:
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
