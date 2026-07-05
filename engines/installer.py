import download_tools as dt


with open("./pack_files/files.xml", 'r') as pack_file:
    pack_list = pack_file.read().split('\n')
    for _ in pack_list:
        if ";" in _:

            url, path, name = _.split(';')
            
            dt.download(url, path, name, skip=True, processes=1)

print("All packs installed.")
