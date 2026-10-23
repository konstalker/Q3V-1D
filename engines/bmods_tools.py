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
            lines = [f'{tag};{name}|{version}\n' for tag, (name, version) in self.mod_info.items()]
            mod_branch.writelines(lines)

        print('saved')

    def __iter__(self):
        return iter(self.mod_info)

    def __contains__(self, x):
        return x in self.mod_list()

    # -----------------------------------------------------------------
    # Tag priority system by branch
    #
    # mod_tree/tag_order.txt is divided into sections [branch]. Within a section -
    # тег на строку, от "базы" к "надстройкам", как раньше: индекс тега
    # внутри своей ветки и есть его приоритет.
    #
    # Not all mods are able to conflict with each other: defrag is a separate folder,
    # never overlapping with osp/compilation; UI skins have their own path set.
    # We don't need the maintainer to decide "defrag above or below compilation?" 
    #
    # Priority is a tuple (branch, index). Comparison makes sense ONLY
    # между тегами одной ветки. Если два мода из разных веток внезапно
    # реально делят файл (build_ownership/_reapply_higher_priority) — это
    # не должно происходить по конфигурации, поэтому в этом случае мы не
    # угадываем победителя, а громко предупреждаем и ничего не трогаем
    # автоматически: это сигнал поправить tag_order.txt, а не тихо
    # разрешаемый конфликт.
    #
    # Register a tag not existing in any branch (a new unregistered mod) to its own unique branch. — то
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
                    print('[warning] tag "{}" is outside any section in {}'.format(line, TAG_ORDER_FILE))

    def reload_tag_order(self):
        self._load_tag_order()

    def priority_of_tag(self, tag):
        """Return (branch, index_within_branch)."""
        for branch, tags in self._tag_order.items():
            if tag in tags:
                return (branch, tags.index(tag))
        print('[warning] tag "{}" not registered in any section of {}'.format(tag, TAG_ORDER_FILE))
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
        # 1. Удаляем запись из self._manifests
        if repo_name in self._manifests:
            del self._manifests[repo_name]
            self._save_all_manifests()
        
        # 2. Также удаляем запись из файла .bmod
        bmod_file = f'./mod_tree/{c_info.mod_branch}.bmod'
        with open(bmod_file, 'r') as rf:
            lines = []
            for line in rf:
                line = line.strip()
                # Запись в формате: tag;branch|version
                if not line or ';' not in line:
                    continue
                try:
                    tag, rest = line.split(';', 1)
                    tag = tag.strip()
                    if tag != repo_name:
                        lines.append(line)
                except:
                    # Если не удалось разбить, оставляем строку
                    lines.append(line)
            
            with open(bmod_file, 'w') as wf:
                wf.writelines(f"{line}\n" for line in lines)

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

                if priority[1] > current_priority[1]:  # БОЛЬШЕЙ индекс побеждает (периферия важнее ядра)
                    owners[path] = (repo_name, priority)
        return owners

    def owner_of(self, path):
        return self.build_ownership().get(_normalize_path(path))

    def check_priority_sanity(self):
        """Not the source of truth for priority (see comment at priority_of_tag) -
        heuristic guide on top of explicit tag_order.txt: within
        one branch, mod with higher priority is usually intended to be
        more focused/specific and logically expects to touch FEWER files
        than what's below it. If opposite and difference is orders of magnitude -
        order in branch is probably swapped. Only prints a warning."""
        for branch, tags in self._tag_order.items():
            sized = []
            for t in tags:
                entry = self.mod_info.get(t)
                if not entry:
                    continue
                repo_name = entry[0]
                if not self.has_manifest(repo_name):
                    continue  # mod appeared before this patch - files not counted, nothing to compare
                sized.append((t, repo_name, len(self.load_manifest(repo_name))))

            for (tag_lo, repo_lo, n_lo), (tag_hi, repo_hi, n_hi) in zip(sized, sized[1:]):
                if n_lo and n_hi and n_hi > n_lo * 5:
                    print('[warning] Branch "{}": {} (tag {}, priority higher) '
                          'touches {}x more files than {} (tag {}, '
                          'priority lower) - typically it should be reversed, check order in tag_order.txt'.format(
                        branch, repo_hi, tag_hi, n_hi // n_lo, repo_lo, tag_lo))


bmod_conf = bmod()
