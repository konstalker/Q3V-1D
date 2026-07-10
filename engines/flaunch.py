import download_tools as dt
from autoupdater import autoupdate
from dmods_tools import *


if not os.path.exists('../baseq3/mods/baseq3'):
    os.mkdir('../baseq3/mods/baseq3')

dmod_conf.save()

list(dt.download('./download_confs/base.dconf', skip=True))

autoupdate()
