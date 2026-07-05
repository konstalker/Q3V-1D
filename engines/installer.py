import download_tools as dt


with open("./pack_files/files.txt", 'r') as pack_file:
    pack_list = pack_file.read().split('\n')
    for _ in pack_list:
        url, path, name = _.split(';')
