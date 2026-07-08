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
    
    def __getitem__(self, key):
        for x in self.mod_info:
            if self.mod_info[x][-1][0] == key:
                return self.mod_info[x][-1][1]
        
        raise KeyError(f'{key} modaification not found in active dmod list')
    
    def mod_list(self):
        
        mods = []

        for x in self.mod_info:
            mods.append(self.mod_info[x][-1][0])

        return mods
        
    def save(self):
        
        with open(f'./mod_tree/{c_info.mod_branch}.dmod', 'w') as mod_branch:
            for x in self.mod_info:
                s = ""
                for y in self.mod_info[x]:
                    s += f';{y[0]}|{y[1]}'
                mod_branch.write(f'{x}{s}\n')


dmod_conf = dmod()
