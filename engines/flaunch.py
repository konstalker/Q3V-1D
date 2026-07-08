import download_tools as dt
from autoupdater import autoupdate

with open('./mod_tree/branch.txt', 'r') as bfile, open('../version', 'r') as vfile:
    text = bfile.read().replace('@', vfile.read().rstrip())

with open('./mod_tree/branch.txt', 'w') as bfile:
    bfile.write(text)

next(dt.download('./download_confs/base.dconf', skip=True, out_data=False))

autoupdate()


# need to write more...
