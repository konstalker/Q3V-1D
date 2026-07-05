import download_tools as dt


with open("./pack_files/files.xml", 'r') as pack_file:
    pack_list = pack_file.read().split('\n')
    for _ in pack_list:
        if ";" in _:

            url, path, name = _.split(';')
            
            dt.download(url, path, name, skip=True)

with open("./pack_files/archieces.xml", 'r') as pack_file:
    pack_list = pack_file.read().split('\n')
    for _ in pack_list:
        if ";" in _:

            files = ['', '']
            
            url, name, files[0], files[1] = _.split(';')
            
            dt.unzip(url, name, files, skip=True)

print("All packs installed.")
