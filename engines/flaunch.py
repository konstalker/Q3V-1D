import download_tools as dt
from upd_tools import autoupdate
from bmods_tools import *


# needed paths

if not os.path.exists('../baseq3/mods/baseq3'):
    os.mkdir('../baseq3/mods/baseq3')

if not os.path.exists('../baseq3/mods/osp/demos'):
    os.mkdir('../baseq3/mods/osp/demos')

if not os.path.exists('./cache'):
    os.mkdir('./cache')


bmod_conf.save()

list(dt.download('./download_confs/base.dconf', skip=True))

autoupdate()
