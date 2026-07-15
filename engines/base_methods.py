from pathlib import Path


def caption():
    print("contacts of creator: https://telegram.me/konstalker")
    print("you can add issue on github: https://github.com/konstalker/Q3V-1D/issues")
    print("thank you for use Q3V#1D")
    input("press enter to continue running")


class C_INFO:
    def __init__(self):
        
        with open('./mod_tree/branch.txt', 'r') as bfile, open('../version', 'r') as vfile, open('../sversion', 'r') as svfile:
            text = bfile.read().replace('@', vfile.read().rstrip()).replace('$', svfile.read().rstrip())
            
        with open('./mod_tree/branch.txt', 'w') as bfile:
            bfile.write(text)
        
        with open("./mod_tree/branch.txt", 'r') as f:
            self.compilation_branch, self.version, self.sversion, self.mod_branch, self.repo_url, self.s_data = f.read().split('\n')[:6]
        self.values = [["[OS]", self.s_data],
                       ["[CBRANCH]", self.compilation_branch],
                       ["[RURL]", self.repo_url]
                      ]

c_info = C_INFO()

def furl(url):
    for x in c_info.values:
        url = url.replace(x[0], x[1])
    return url


def get_relative_paths(folder_path: str) -> list[str]:
    base_dir = Path(folder_path)
    relative_paths = []
    
    for item in base_dir.rglob('*'):
        if item.is_file():
            rel_path = item.relative_to(base_dir)
            relative_paths.append(f"/{rel_path.as_posix()}")
            
    return relative_paths
