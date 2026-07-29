"""
Минималистичная база GUI на tkinter (встроенная библиотека Python).

Возможности:
    - Система СТРАНИЦ: наследуешь класс Page, размещаешь на ней любые
      виджеты, регистрируешь через app.add_page(...) — пункт меню
      и переключение страниц настраиваются сами.
    - DataTable  — таблица с вертикальной и горизонтальной прокруткой.
      Данные передаются в любой момент: set_data(...) / add_row(...).
    - LiveLabel  — карточка "заголовок + значение", значение обновляется
      мгновенно вызовом .set(новое_значение) откуда угодно в коде.
    - LiveText   — текстовое поле-лог с прокруткой, .append(строка)
      добавляет текст и сама прокручивается вниз.

Палитра:
    чёрный / тёмно-серый — фон и панели
    красный              — основной акцент
    бирюзовый            — редкий акцент (индикатор статуса)

Важно про потоки: tkinter не потокобезопасен. Если данные приходят
из фонового потока (сеть, сенсор, таймер не через tkinter), обновляйте
виджеты так:  widget.after(0, lambda: widget.set(value))

Запуск:  python gui_framework.py
"""

import tkinter as tk
from tkinter import ttk

# ============================== ПАЛИТРА ==============================
BG_MAIN   = "#0e0e0e"
BG_PANEL  = "#161616"
BG_HOVER  = "#232323"
BORDER    = "#262626"

FG_TEXT   = "#e8e8e8"
FG_MUTED  = "#8a8a8a"
FG_BRIGHT = "#ffffff"

RED       = "#e6435a"
RED_HOVER = "#ff5468"
RED_PRESS = "#c93247"
RED_DIM   = "#3a1620"   # приглушённый красный — для выделения строк в таблице

TEAL      = "#2dd4bf"   # бирюзовый — используется очень редко

FONT_MAIN  = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI Semibold", 16)
FONT_BIG   = ("Segoe UI Semibold", 20)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 10)


def setup_style(root):
    """Настраивает всю тёмную тему один раз при старте приложения."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=BG_MAIN)
    style.configure("TLabel", background=BG_MAIN, foreground=FG_TEXT, font=FONT_MAIN)
    style.configure("Muted.TLabel", background=BG_MAIN, foreground=FG_MUTED, font=FONT_SMALL)
    style.configure("Title.TLabel", background=BG_MAIN, foreground=FG_BRIGHT, font=FONT_TITLE)

    # --- кнопки навигации ---
    style.configure("Nav.TButton", background=BG_PANEL, foreground=FG_TEXT,
                     borderwidth=0, font=FONT_MAIN, padding=(16, 10), anchor="w")
    style.map("Nav.TButton",
              background=[("active", BG_HOVER), ("pressed", BG_HOVER)],
              foreground=[("active", FG_BRIGHT)])

    style.configure("NavActive.TButton", background=BG_HOVER, foreground=FG_BRIGHT,
                     borderwidth=0, font=FONT_MAIN, padding=(16, 10), anchor="w")
    style.map("NavActive.TButton", background=[("active", BG_HOVER)])

    # --- акцентная кнопка ---
    style.configure("Accent.TButton", background=RED, foreground=FG_BRIGHT,
                     borderwidth=0, font=FONT_MAIN, padding=(16, 9))
    style.map("Accent.TButton", background=[("active", RED_HOVER), ("pressed", RED_PRESS)])

    # --- таблица (Treeview) ---
    style.configure("Treeview",
                     background=BG_PANEL, fieldbackground=BG_PANEL, foreground=FG_TEXT,
                     rowheight=28, font=FONT_MAIN, borderwidth=0)
    style.map("Treeview",
              background=[("selected", RED_DIM)],
              foreground=[("selected", FG_BRIGHT)])

    style.configure("Treeview.Heading",
                     background=BG_HOVER, foreground=FG_TEXT,
                     font=("Segoe UI Semibold", 10), borderwidth=0, relief="flat")
    style.map("Treeview.Heading", background=[("active", BG_HOVER)])

    # --- полосы прокрутки ---
    for orient in ("Vertical", "Horizontal"):
        style.configure(f"{orient}.TScrollbar",
                         background=BG_HOVER, troughcolor=BG_MAIN,
                         bordercolor=BG_MAIN, arrowcolor=FG_MUTED, relief="flat")
        style.map(f"{orient}.TScrollbar", background=[("active", BG_HOVER)])


# ============================ ЭЛЕМЕНТЫ ============================

class LiveLabel(tk.Frame):
    """
    Карточка "заголовок + значение". Значение можно обновлять
    в любой момент из кода — это и есть "реальное время".

        speed = LiveLabel(parent, title="Скорость", value="0 км/ч")
        speed.pack()
        ...
        speed.set("87 км/ч")   # обновление откуда угодно
    """

    def __init__(self, parent, title="", value="", accent=RED):
        super().__init__(parent, bg=BG_PANEL, padx=20, pady=16)
        tk.Label(self, text=title, bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL).pack(anchor="w")

        self._value_var = tk.StringVar(value=value)
        tk.Label(self, textvariable=self._value_var, bg=BG_PANEL,
                  fg=FG_BRIGHT, font=FONT_BIG).pack(anchor="w", pady=(6, 0))

        tk.Frame(self, bg=accent, height=3, width=36).pack(anchor="w", pady=(12, 0))

    def set(self, value):
        """Мгновенно обновляет отображаемое значение."""
        self._value_var.set(str(value))

    def get(self):
        return self._value_var.get()


class LiveText(tk.Frame):
    """
    Текстовое поле-лог с прокруткой, для вывода, который дополняется
    в реальном времени (события, сообщения, показания датчиков и т.п.).

        log = LiveText(parent, height=12)
        log.pack(fill="both", expand=True)
        ...
        log.append("Соединение установлено")   # добавить строку
        log.set_text("...")                     # заменить всё содержимое
        log.clear()                             # очистить
    """

    def __init__(self, parent, height=10):
        super().__init__(parent, bg=BG_PANEL)
        self.text = tk.Text(self, height=height, bg=BG_PANEL, fg=FG_TEXT,
                             font=FONT_MONO, bd=0, highlightthickness=0,
                             wrap="word", insertbackground=FG_TEXT, state="disabled")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)

        self.text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def append(self, line):
        """Добавляет новую строку в конец и прокручивает вниз."""
        self.text.configure(state="normal")
        self.text.insert("end", str(line) + "\n")
        self.text.see("end")
        self.text.configure(state="disabled")

    def set_text(self, content):
        """Полностью заменяет содержимое поля."""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", str(content))
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self):
        self.set_text("")


class DataTable(tk.Frame):
    """
    Таблица с вертикальной и горизонтальной прокруткой.
    Столбцы задаются один раз при создании, данные — когда угодно.

        table = DataTable(parent, columns=[
            {"key": "name",  "title": "Имя",   "width": 200},
            {"key": "score", "title": "Счёт",  "width": 100, "anchor": "center"},
        ])
        table.pack(fill="both", expand=True)

        table.set_data([
            {"name": "Аня", "score": 87},
            {"name": "Игорь", "score": 92},
        ])
        table.add_row({"name": "Новый игрок", "score": 0})   # добавить строку
        table.clear()                                        # очистить всё
    """

    def __init__(self, parent, columns):
        super().__init__(parent, bg=BG_PANEL)
        self.columns = columns
        keys = [c["key"] for c in columns]

        self.tree = ttk.Treeview(self, columns=keys, show="headings")
        for c in columns:
            self.tree.heading(c["key"], text=c.get("title", c["key"]))
            self.tree.column(c["key"], width=c.get("width", 120),
                              anchor=c.get("anchor", "w"))

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def set_data(self, rows):
        """Полностью заменяет содержимое. rows — список словарей {key: значение}."""
        self.clear()
        for row in rows:
            self.add_row(row)

    def add_row(self, row):
        """Добавляет одну строку (словарь {key: значение}) в конец таблицы."""
        values = [row.get(c["key"], "") for c in self.columns]
        return self.tree.insert("", "end", values=values)

    def update_row(self, item_id, row):
        """Обновляет уже вставленную строку по её id (возвращается из add_row)."""
        values = [row.get(c["key"], "") for c in self.columns]
        self.tree.item(item_id, values=values)

    def remove_selected(self):
        """Удаляет выбранную строку, если есть."""
        for item in self.tree.selection():
            self.tree.delete(item)

    def get_selected(self):
        """Возвращает значения выбранной строки (или None)."""
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


# ============================ СТРАНИЦЫ ============================

class Page(tk.Frame):
    """
    Базовый класс страницы. Чтобы сделать свою страницу:

        class MyPage(Page):
            def setup(self):
                ttk.Label(self, text="Заголовок", style="Title.TLabel").pack(
                    anchor="w", padx=28, pady=20)
                # дальше — любые виджеты, DataTable, LiveLabel, LiveText...

    Затем зарегистрировать в приложении:  app.add_page("Имя в меню", MyPage)
    """

    def __init__(self, master, app):
        super().__init__(master, bg=BG_MAIN)
        self.app = app  # ссылка на главное приложение
        self.setup()

    def setup(self):
        """Переопределите: здесь создаются и размещаются виджеты страницы."""
        pass

    def on_show(self):
        """Необязательно: вызывается каждый раз при переходе на эту страницу."""
        pass


class PageManager(tk.Frame):
    """Контейнер, который хранит все страницы друг над другом и переключает их."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_MAIN)
        self.pages = {}
        self.current = None

    def register(self, name, page):
        self.pages[name] = page
        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        if self.current is None:
            self.show(name)

    def show(self, name):
        page = self.pages.get(name)
        if page is None:
            return
        page.tkraise()
        self.current = name
        page.on_show()


# ======================== ПРИМЕРЫ СТРАНИЦ ========================
# Можно смело удалить эти три класса и написать свои — механизм тот же.

class DashboardPage(Page):
    def setup(self):
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=28, pady=(20, 10))
        ttk.Label(header, text="Главная", style="Title.TLabel").pack(side="left")

        cards = tk.Frame(self, bg=BG_MAIN)
        cards.pack(fill="x", padx=28, pady=(0, 20))

        self.clock = LiveLabel(cards, title="Время", value="--:--:--")
        self.clock.pack(side="left", padx=(0, 14))

        self.counter = LiveLabel(cards, title="Тактов", value="0", accent=TEAL)
        self.counter.pack(side="left")

        self._ticks = 0
        self._tick()

    def _tick(self):
        import datetime
        self.clock.set(datetime.datetime.now().strftime("%H:%M:%S"))
        self._ticks += 1
        self.counter.set(self._ticks)
        self.after(1000, self._tick)  # повторять каждую секунду


class TablePage(Page):
    def setup(self):
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=28, pady=(20, 10))
        ttk.Label(header, text="Проекты", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="+ Добавить", style="Accent.TButton",
                    command=self._add_row).pack(side="right")
        ttk.Button(header, text="Удалить выбранное", style="Nav.TButton",
                    command=lambda: self.table.remove_selected()).pack(side="right", padx=8)

        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        self.table = DataTable(body, columns=[
            {"key": "name",     "title": "Проект",   "width": 240, "anchor": "w"},
            {"key": "status",   "title": "Статус",   "width": 140, "anchor": "w"},
            {"key": "progress", "title": "Прогресс", "width": 100, "anchor": "center"},
        ])
        self.table.pack(fill="both", expand=True)

        self.table.set_data([
            {"name": "Редизайн сайта",       "status": "В работе",     "progress": "45%"},
            {"name": "Мобильное приложение", "status": "Планирование", "progress": "10%"},
            {"name": "API v2",               "status": "Готово",       "progress": "100%"},
        ])

    def _add_row(self):
        import random
        names = ["Новый модуль", "Интеграция", "Тестирование", "Оптимизация"]
        statuses = ["В работе", "На проверке", "Планирование"]
        self.table.add_row({
            "name": random.choice(names),
            "status": random.choice(statuses),
            "progress": f"{random.randint(0, 100)}%",
        })


class LogPage(Page):
    def setup(self):
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=28, pady=(20, 10))
        ttk.Label(header, text="Аналитика", style="Title.TLabel").pack(side="left")

        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        self.log = LiveText(body, height=14)
        self.log.pack(fill="both", expand=True)

        self._n = 0
        self._feed()

    def _feed(self):
        self._n += 1
        self.log.append(f"[{self._n:03}] событие обработано")
        self.after(1500, self._feed)  # раз в 1.5 секунды приходит "новое событие"


class SettingsPage(Page):
    def setup(self):
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill="x", padx=28, pady=(20, 10))
        ttk.Label(header, text="Настройки", style="Title.TLabel").pack(side="left")

        body = tk.Frame(self, bg=BG_MAIN)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        ttk.Label(body, text="Здесь можно разместить свои элементы:\nполя ввода, чекбоксы, переключатели и т.д.",
                    style="Muted.TLabel", justify="left").pack(anchor="w")


# ============================== ПРИЛОЖЕНИЕ ==============================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minimal UI")
        self.geometry("1040x640")
        self.minsize(820, 520)
        self.configure(bg=BG_MAIN)

        setup_style(self)
        self._build_shell()

        # --- регистрация страниц: добавляйте свои так же ---
        self.add_page("Главная", DashboardPage)
        self.add_page("Проекты", TablePage)
        self.add_page("Аналитика", LogPage)
        self.add_page("Настройки", SettingsPage)

    def _build_shell(self):
        """Создаёт сайдбар и область страниц (общий каркас окна)."""
        self.sidebar = tk.Frame(self, bg=BG_PANEL, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_row = tk.Frame(self.sidebar, bg=BG_PANEL, height=64)
        logo_row.pack(fill="x")
        tk.Label(logo_row, text="●  MINIMAL", bg=BG_PANEL, fg=RED,
                  font=("Segoe UI Semibold", 13)).pack(side="left", padx=18, pady=18)

        # редкий бирюзовый акцент — индикатор статуса, закреплён снизу
        status_row = tk.Frame(self.sidebar, bg=BG_PANEL)
        status_row.pack(side="bottom", fill="x", pady=18, padx=18)
        dot = tk.Canvas(status_row, width=8, height=8, bg=BG_PANEL, highlightthickness=0)
        dot.create_oval(0, 0, 8, 8, fill=TEAL, outline="")
        dot.pack(side="left")
        tk.Label(status_row, text="в сети", bg=BG_PANEL, fg=FG_MUTED,
                  font=FONT_SMALL).pack(side="left", padx=8)

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(side="bottom", fill="x", pady=(0, 14), padx=10)

        self.nav_container = tk.Frame(self.sidebar, bg=BG_PANEL)
        self.nav_container.pack(fill="x")
        self.nav_buttons = {}

        self.page_area = PageManager(self)
        self.page_area.pack(side="left", fill="both", expand=True)

    def add_page(self, name, page_class):
        """
        Регистрирует новую страницу и создаёт для неё пункт меню.
        page_class — класс, унаследованный от Page.
        """
        page = page_class(self.page_area, self)
        self.page_area.register(name, page)

        is_first = len(self.nav_buttons) == 0
        style_name = "NavActive.TButton" if is_first else "Nav.TButton"
        btn = ttk.Button(self.nav_container, text=name, style=style_name,
                          command=lambda n=name: self._select_nav(n))
        btn.pack(fill="x", padx=10, pady=2)
        self.nav_buttons[name] = btn

    def _select_nav(self, name):
        for n, btn in self.nav_buttons.items():
            btn.configure(style="NavActive.TButton" if n == name else "Nav.TButton")
        self.page_area.show(name)


if __name__ == "__main__":
    App().mainloop()
