from base_methods import *
import os

MANIFEST_FILE = f'./mod_tree/{c_info.mod_branch}.tree'
TAG_ORDER_FILE = './mod_tree/tag_order.txt'


# ---------------------------------------------------------------------------
# Формат дерева файлов: обычный текст с отступом табом на уровень
# вложенности, вместо JSON. Один файл (MANIFEST_FILE) на ВСЕ моды —
# верхний уровень дерева это имя мода, дальше — обычное поддерево путей.
# Почему так, а не N файлов (по одному на мод) и не JSON:
#   - один read/write вместо N файловых операций на каждую проверку
#     владения — bmod читает файл один раз при старте и держит в памяти;
#   - для больших сборок (тысячи файлов) не дублирует общий префикс пути
#     на каждой строке, как это делал бы плоский список или JSON-массив;
#   - тривиально читается/дифается глазами и грепается, без парсера.
#
# Важно: хранится СПИСОК ФАЙЛОВ КАЖДОГО МОДА, а не "текущий победитель"
# на путь. Владение (build_ownership) — это ВЫЧИСЛЯЕМОЕ представление
# поверх этих списков + приоритетов тегов, а не отдельно хранимые данные.
# Если бы вместо списков хранился только текущий владелец пути, при
# удалении более приоритетного мода не было бы способа узнать, что
# менее приоритетный мод тоже предоставлял этот файл и должен его
# унаследовать обратно — пришлось бы заново скачивать/распаковывать
# мод только ради восстановления того, что и так уже стояло на диске.
#
# Пример (кусок общего файла):
#   kon
#   \tbaseq3
#   \t\tmods
#   \t\t\tosp
#   \t\t\t\tzzz-kon.pk3dir
#   \t\t\t\t\tmodels
#   \t\t\t\t\t\tweapons2
#   \t\t\t\t\t\t\trocketl
#   \t\t\t\t\t\t\t\trocketl.md3
#   GothicRL
#   \tbaseq3
#   \t\tmods
#   \t\t\tosp
#   \t\t\t\tzzz_GothicRL.pk3
# ---------------------------------------------------------------------------

def _normalize_path(path):
    return os.path.normpath(path).replace('\\', '/')


def _paths_to_tree(paths):
    root = {}
    for p in paths:
        parts = [part for part in _normalize_path(p).split('/') if part and part != '.']
        node = root
        for part in parts:
            node = node.setdefault(part, {})
    return root


def _tree_to_lines(tree, depth=0):
    lines = []
    for name in sorted(tree.keys()):
        lines.append('\t' * depth + name)
        children = tree[name]
        if children:
            lines.extend(_tree_to_lines(children, depth + 1))
    return lines


def tree_text(paths):
    """Плоский список путей -> текст дерева с отступами."""
    return '\n'.join(_tree_to_lines(_paths_to_tree(paths)))


def text_to_tree(text):
    """Текст дерева с отступами -> вложенный dict."""
    root = {}
    stack = [(-1, root)]
    for raw_line in text.split('\n'):
        if not raw_line.strip('\t').strip():
            continue
        stripped = raw_line.lstrip('\t')
        depth = len(raw_line) - len(stripped)
        name = stripped.rstrip('\n')
        while stack and stack[-1][0] >= depth:
            stack.pop()
        parent = stack[-1][1] if stack else root
        node = parent.setdefault(name, {})
        stack.append((depth, node))
    return root


def tree_to_paths(tree, prefix=''):
    """Вложенный dict -> плоский список путей (для сравнения владения файлами)."""
    paths = []
    for name, children in tree.items():
        full = f'{prefix}/{name}' if prefix else name
        if children:
            paths.extend(tree_to_paths(children, full))
        else:
            paths.append(full)
    return paths


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

        self._load_tag_order()
        self._manifests = self._load_all_manifests()

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

    # -----------------------------------------------------------------
    # Приоритет по тегам, с ветками
    #
    # mod_tree/tag_order.txt разбит на секции [branch]. Внутри секции —
    # тег на строку, от "базы" к "надстройкам", как раньше: индекс тега
    # внутри своей ветки и есть его приоритет.
    #
    # Ветки нужны потому, что не все моды вообще способны конфликтовать
    # друг с другом: defrag — отдельная папка мода, никогда не пересекается
    # по файлам с содержимым osp/compilation; UI-скины — свой набор путей.
    # Заставлять мейнтейнера решать "defrag выше или ниже compilation?"
    # бессмысленно, если они физически не могут перекрыть друг друга.
    #
    # Приоритет — это tuple (branch, index). Сравнение имеет смысл ТОЛЬКО
    # между тегами одной ветки. Если два мода из разных веток внезапно
    # реально делят файл (build_ownership/_reapply_higher_priority) — это
    # не должно происходить по конфигурации, поэтому в этом случае мы не
    # угадываем победителя, а громко предупреждаем и ничего не трогаем
    # автоматически: это сигнал поправить tag_order.txt, а не тихо
    # разрешаемый конфликт.
    #
    # Тег, которого нет ни в одной ветке (новый мод, который никто не
    # зарегистрировал), получает свою СОБСТВЕННУЮ уникальную ветку — то
    # есть по умолчанию гарантированно ни с кем не сравнивается. Раньше
    # такой тег молча уезжал в конец общего списка (максимальный
    # приоритет) — теперь вместо этого при реальном пересечении файлов
    # вы увидите предупреждение и явно решите, куда его вписать.
    # -----------------------------------------------------------------

    def _load_tag_order(self):
        self._tag_order = {}  # branch_name -> [tags по возрастанию приоритета]

        if not os.path.exists(TAG_ORDER_FILE):
            return

        branch = None
        with open(TAG_ORDER_FILE, 'r') as f:
            for raw_line in f.read().split('\n'):
                line = raw_line.split('#', 1)[0].strip()  # '#' - комментарии
                if not line:
                    continue
                if line.startswith('[') and line.endswith(']'):
                    branch = line[1:-1].strip()
                    self._tag_order.setdefault(branch, [])
                elif branch is not None:
                    self._tag_order[branch].append(line)
                else:
                    print(f'[warning] тег "{line}" в {TAG_ORDER_FILE} указан вне секции '
                          f'[branch] — игнорирую, оберните его в секцию')

    def reload_tag_order(self):
        self._load_tag_order()

    def priority_of_tag(self, tag):
        """Возвращает (branch, index_внутри_branch)."""
        for branch, tags in self._tag_order.items():
            if tag in tags:
                return (branch, tags.index(tag))
        print(f'[warning] tag "{tag}" не зарегистрирован ни в одной ветке {TAG_ORDER_FILE} — '
              f'помещаю в отдельную ветку "unregistered:{tag}" (по умолчанию ни с кем не сравнивается)')
        return (f'unregistered:{tag}', 0)

    def priority_of(self, repo_name, modlist=None):
        """Приоритет мода. Для уже установленного мода тег известен из
        собственного состояния bmod; для ещё не установленного нужно
        передать modlist (index.json), чтобы узнать его тег."""
        for tag, (name, _version) in self.mod_info.items():
            if name == repo_name:
                return self.priority_of_tag(tag)

        if modlist and repo_name in modlist:
            return self.priority_of_tag(modlist[repo_name]['tag'])

        raise KeyError(
            f'{repo_name} не установлен и modlist не передан — не могу узнать тег/приоритет'
        )

    # -----------------------------------------------------------------
    # Манифесты (дерево файлов, которые реально положил на диск мод) —
    # все моды в одном файле (MANIFEST_FILE), читается один раз при
    # старте и держится в памяти (self._manifests); каждое изменение
    # перезаписывает файл целиком (install/remove — редкие операции,
    # цена одной перезаписи против постоянных построчных чтений N
    # файлов при каждой проверке владения — того стоит).
    #
    # На первой установке мода записи о нём ещё нет — это не ошибка,
    # load_manifest() в этом случае просто вернёт пустой список.
    # Манифест появляется только как побочный продукт настоящей
    # установки: download() распаковывает .dconf и возвращает точный
    # список того, что легло на диск, а save_manifest() это фиксирует.
    # Никакого отдельного "предсказания" дерева до реальной установки
    # не делается — источник истины всегда только уже свершившаяся
    # распаковка.
    # -----------------------------------------------------------------

    def _load_all_manifests(self):
        if not os.path.exists(MANIFEST_FILE):
            return {}
        with open(MANIFEST_FILE, 'r') as f:
            tree = text_to_tree(f.read())
        return {repo_name: tree_to_paths(subtree) for repo_name, subtree in tree.items()}

    def _save_all_manifests(self):
        tree = {repo_name: _paths_to_tree(paths) for repo_name, paths in self._manifests.items()}
        os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
        with open(MANIFEST_FILE, 'w') as f:
            f.write('\n'.join(_tree_to_lines(tree)))

    def has_manifest(self, repo_name):
        return bool(self._manifests.get(repo_name))

    def save_manifest(self, repo_name, files):
        """files — плоский список путей, как их возвращает download_tools.download()."""
        self._manifests[repo_name] = sorted(set(_normalize_path(f) for f in files if f))
        self._save_all_manifests()

    def load_manifest(self, repo_name):
        """Плоский список путей мода. [] если манифеста ещё нет (первая установка)."""
        return list(self._manifests.get(repo_name, []))

    def load_manifest_tree(self, repo_name):
        """Вложенный dict — удобно для GUI (чекбоксы по папкам, "половина сборки")."""
        return _paths_to_tree(self._manifests.get(repo_name, []))

    def delete_manifest(self, repo_name):
        if repo_name in self._manifests:
            del self._manifests[repo_name]
            self._save_all_manifests()

    # -----------------------------------------------------------------
    # Владение файлами
    #
    # Для каждого пути на диске — какой активный мод им сейчас "владеет"
    # (с каким приоритетом). Считается из манифестов + приоритетов тегов
    # всех активных модов, без обращения к сети и .dconf.
    # -----------------------------------------------------------------

    def build_ownership(self):
        """path -> (repo_name, priority) для всех активных модов.
        При пересечении путей внутри одной ветки побеждает более высокий
        индекс. Пересечение между РАЗНЫМИ ветками не должно происходить
        по конфигурации — вместо угадывания победителя печатается
        предупреждение, текущий владелец не меняется."""
        owners = {}
        for tag, (repo_name, _version) in self.mod_info.items():
            priority = self.priority_of_tag(tag)
            for path in self.load_manifest(repo_name):
                current = owners.get(path)
                if current is None:
                    owners[path] = (repo_name, priority)
                    continue

                current_repo, current_priority = current
                if current_repo == repo_name:
                    continue

                if current_priority[0] != priority[0]:
                    print(f'[warning] {path}: делят {current_repo} (ветка {current_priority[0]}) '
                          f'и {repo_name} (ветка {priority[0]}) — ветки не связаны в tag_order.txt, '
                          f'оставляю текущего владельца')
                    continue

                if current_priority[1] <= priority[1]:
                    owners[path] = (repo_name, priority)
        return owners

    def owner_of(self, path):
        return self.build_ownership().get(_normalize_path(path))

    def check_priority_sanity(self):
        """Не источник истины для приоритета (см. комментарий у priority_of_tag) —
        просто эвристическая подсказка поверх явного tag_order.txt: внутри
        одной ветки мод с более высоким приоритетом обычно задуман как более
        точечный/специфичный и логично ожидать, что он трогает МЕНЬШЕ файлов,
        чем то, что стоит под ним. Если наоборот и разница в разы — вероятно,
        порядок в ветке перепутан местами. Только печатает предупреждение."""
        for branch, tags in self._tag_order.items():
            sized = []
            for t in tags:
                entry = self.mod_info.get(t)
                if not entry:
                    continue
                repo_name = entry[0]
                if not self.has_manifest(repo_name):
                    continue  # мод стоял до этого патча — файлы не посчитаны, сравнивать не с чем
                sized.append((t, repo_name, len(self.load_manifest(repo_name))))

            for (tag_lo, repo_lo, n_lo), (tag_hi, repo_hi, n_hi) in zip(sized, sized[1:]):
                if n_lo and n_hi and n_hi > n_lo * 5:
                    print(f'[warning] ветка "{branch}": {repo_hi} (тег {tag_hi}, приоритет выше) '
                          f'трогает в {n_hi // n_lo}x больше файлов, чем {repo_lo} (тег {tag_lo}, '
                          f'приоритет ниже) — обычно бывает наоборот, проверьте порядок в tag_order.txt')


bmod_conf = bmod()
