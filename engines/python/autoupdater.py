from base_methods import *
from upd_tools import *
from dmods_tools import *


def autoupdate():
    if not os.path.exists("./temp_files"):
        os.mkdir("./temp_files")

    dt.downloader(furl('[RURL]index.modlist'), "./temp_files/", "modlist.txt", skip=True)
   
    with open("./temp_files/modlist.txt", 'r') as f:
        for x in dmod_conf.mod_list():
            update(x)

    dmod_conf.save()

    try:
        shutil.rmtree("./temp_files/")
    except Exception:
        pass


if __name__ == "__main__":
    autoupdate()
