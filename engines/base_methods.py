def caption():
    print("contacts of creator: https://t.me/konstalker")
    print("you can add issue on github: https://github.com/konstalker/Q3V-1D/issues")
    print("thank you for use Q3V#1D")
    input("press enter to continue running")


class C_INFO:
    def __init__(self):
        with open("./mod_tree/branch.txt", 'r') as f:
            self.compilation_branch, self.version, self.mod_branch, self.repo_url, self.s_data = f.read().split('\n')[:5]
        self.values = [["[OS]", self.s_data],
                       ["[CBRANCH]", self.compilation_branch],
                       ["[RURL]", self.repo_url]
                      ]

    def __call__(self, url):

        for x in self.values:
            url = url.replace(x[0], x[1])
        return url
    

furl = C_INFO()
c_info = C_INFO()
