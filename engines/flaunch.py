import download_tools as dt
from autoupdater import autoupdate

with open('./mod_tree/branch.txt', 'r') as bfile, open('../version', 'r') as vfile, open('../sversion', 'r') as svfile:
    text = bfile.read().replace('@', vfile.read().rstrip())
    text = bfile.read().replace('$', svfile.read().rstrip())

with open('./mod_tree/branch.txt', 'w') as bfile:
    bfile.write(text)

dt.download('./download_confs/base.dconf', skip=True, out_data=False)

autoupdate()


# need to write more...
