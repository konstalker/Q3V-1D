import download_tools as dt


with open("./pack_files/files.xml", 'r') as pack_file:
    pack_list = pack_file.read().split('\n')
    for _ in pack_list:
        if ";" in _:

            url, path, name = _.split(';')
            
            dt.download(url, path, name, skip=True)

with open("./pack_files/archieves.xml", 'r') as pack_file:
    pack_list = pack_file.read().split('\n')
    for _ in pack_list:
        if ";" in _:

            files = []
            
            arr = _.split(';')
            url, name = arr[0], arr[1]

            for x, y in zip(arr[2::2], arr[3::2]):
                files.append([x, y])
            
            dt.unzip(url, name, files, skip=True)

print("All packs installed.")
