from base_methods import *
import os


class bmod:
    def __init__(self):

        with open(f"./mod_tree/{c_info.mod_branch}.bmod", 'r') as mod_branch:
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

                    if mods[-1][1] == '$':
                        if len(line) == i + 1:
                            mods[-1][1] = c_info.sversion
                        else:
                            mods[-1][1] = "0"

                self.mod_info.update({tag: mods})
    
    def __getitem__(self, key):
        for x in self.mod_info:
            if self.mod_info[x][-1][0] == key:
                return self.mod_info[x][-1][1]
                    
        return '0'

    def __setitem__(self, key, value):

        value, tag = value

        if tag in self.mod_info:
            
            position = -1
            for i, x in enumerate(self.mod_info[tag]):
                if x[0] == key:
                    position = i
                    break
            
            if position >= 0:
                self.mod_info[tag][position] = [key, None]
                if value == None:
                    self.mod_info[tag].pop(position)
                    if not self.mod_info[tag]:
                        self.mod_info.pop(tag)
                else:
                    self.mod_info[tag][position][1] = value
            elif value != None:
                self.mod_info[tag].append([key, value])
                
        elif value != None:
            self.mod_info.update({tag: [[key, value]]})
    
    def mod_list(self):
        
        mods = []

        for x in self.mod_info:
            mods.append(self.mod_info[x][-1][0])

        return mods
        
    def save(self):

        print('saving')
        
        with open(f'./mod_tree/{c_info.mod_branch}.bmod', 'w') as mod_branch:
            for x in self.mod_info:
                s = ""
                for y in self.mod_info[x]:
                    s += f';{y[0]}|{y[1]}'
                mod_branch.write(f'{x}{s}\n')

        print('saved')
    
    def __iter__(self):
        return self.mod_info


bmod_conf = bmod()
