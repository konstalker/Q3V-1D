import download_tools as dt

with open('./mod_tree/branch.txt', 'r') as bfile, open('../version.txt', 'r') as vfile:
    text = bfile.read().replace('@', vfile.read().rstrip())

with open('./mod_tree/branch.txt', 'w') as bfile:
    bfile.write(text)


dt.download('./download_confs/base.dconf', skip=True)

# need to write more...
