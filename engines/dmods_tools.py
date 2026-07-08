from base_methods import *

import os


class dmod:
    def __init__(self, mod_name):
        with open(f"./mod_tree/{mod_name}.dmod") as mod_branch:
            
