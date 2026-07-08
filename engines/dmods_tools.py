from base_methods import *

import os


class dmod:
    def __init__(self):

        with open(f"./mod_tree/{c_info.mod_branch}.dmod", 'r') as mod_branch:
            self.mod_info = {}

            mod_branch = list(mod_branch.read().rstrip().split('\n'))

            for line in mod_branch:
                line = list(line.split(';'))
                tag, line, mods = line[0], line[1:], []
                
                for i, x in enumerate(line):
                    mods.append(list(x.split('|')))
                    
                    if mods[-1][1] == '@':
                        if len(line) == i + 1:
                            mods[-1][1] = c_info.version
                        else:
                            mods[-1][1] = "0"

                self.mod_info.update({tag: mods})
        

if __name__ == '__main__':
    main = dmod()
    print(*list(map(lambda x: f"{x}: {main.mod_info[x]}", main.mod_info)), sep='\n')