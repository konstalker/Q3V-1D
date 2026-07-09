import download_tools as dt
from autoupdater import autoupdate
from dmods_tools import *

dmod_conf.save()

next(dt.download('./download_confs/base.dconf', skip=True, out_data=False))

autoupdate()
