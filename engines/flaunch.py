import download_tools as dt
from launch import autoupdate
from dmods_tools import *


if not os.path.exists('../baseq3/mods/baseq3'):
    os.mkdir('../baseq3/mods/baseq3')

if not os.path.exists('./cache'):
    os.mkdir('./cache')


dmod_conf.save()

list(dt.download('./download_confs/base.dconf', skip=True))

autoupdate()
