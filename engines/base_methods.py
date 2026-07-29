from pathlib import Path
import urllib.request
import urllib.error
from tkinter import END

def check_url(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        return response.status == 200
    except Exception:
        return False

def caption():
    print("contacts of creator: https://telegram.me/konstalker")
    print("you can add issue on github: https://github.com/konstalker/Q3V-1D/issues")
    print("thank you for use Q3V#1D")

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


class RedirectToText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # Приводим \r\n → \n
        string = string.replace('\r\n', '\n')

        while '\r' in string:
            before, after = string.split('\r', 1)

            # Вставляем текст до \r
            if before:
                self.text_widget.insert(END, before)

            # --- Главное исправление ---
            # Проверяем, чем заканчивается текст
            if self.text_widget.index("end-1c") != "1.0":
                last_char = self.text_widget.get("end-2c")  # символ перед самым концом

                # Если последний символ НЕ перевод строки —
                # значит мы находимся внутри строки и её нужно очистить
                if last_char != '\n':
                    line_start = self.text_widget.index("end-1c linestart")
                    self.text_widget.delete(line_start, "end-1c")
            # -----------------------------

            string = after

        # Обычный текст (без \r)
        if string:
            self.text_widget.insert(END, string)

        self.text_widget.see(END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass


if __name__ == "__main__":
    print(check_url('git'))
