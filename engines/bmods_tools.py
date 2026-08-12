from base_methods import *
import os


class bmod:
    """
    Хранит по одному активному моду на тег: {tag: [name, version]}.
    Инвариант "1 тег — 1 мод" соблюдается на уровне __setitem__: установка
    нового мода под тем же тегом просто перезаписывает запись, старое имя
    там больше не значится установленным (реальное удаление файлов —
    забота вызывающего кода, см. upd_tools.update()).
    """

    def __init__(self):
        with open(f"./mod_tree/{c_info.mod_branch}.bmod", 'r') as mod_branch:
            self.mod_info = {}
            
            with open('../version', 'r') as vfile, open('../sversion', 'r') as svfile:
                v, sv =  vfile.read().rstrip(), svfile.read().rstrip()

            for line in mod_branch.read().rstrip().split('\n'):
                if not line:
                    continue

                parts = line.split(';')
                tag, entries = parts[0], parts[1:]

                # На тег допустима только одна активная запись — берём последнюю.
                # Более ранние записи (могли остаться в файле со старого формата,
                # где на тег было по несколько записей) отбрасываем как неактуальные.
                name, version = entries[-1].split('|')

                if version == '@':
                    version = v
                elif version == '$':
                    version = sv

                self.mod_info[tag] = [name, version]

    def __getitem__(self, key):
        for name, version in self.mod_info.values():
            if name == key:
                return version
        return '0'

    def __setitem__(self, key, value):
        """
        bmod_conf[key] = version, tag

        version is not None -> key становится единственным модом под этим tag
                                (полностью заменяет то, что там было).
        version is None     -> запись тега стирается целиком (тег снова
                                свободен), но только если key совпадает с
                                текущим активным модом этого tag (защита от
                                случайной отмены чужой/более новой записи).
        """
        version, tag = value

        if version is None:
            current = self.mod_info.get(tag)
            if current and current[0] == key:
                del self.mod_info[tag]
            return

        self.mod_info[tag] = [key, version]

    def mod_list(self):
        return [name for name, version in self.mod_info.values()]

    def save(self):
        print('saving')

        with open(f'./mod_tree/{c_info.mod_branch}.bmod', 'w') as mod_branch:
            for tag, (name, version) in self.mod_info.items():
                mod_branch.write(f'{tag};{name}|{version}\n')

        print('saved')

    def __iter__(self):
        return iter(self.mod_info)

    def __contains__(self, x):
        return x in self.mod_list()


bmod_conf = bmod()
