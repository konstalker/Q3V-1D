import tkinter as tk


class Page(tk.Frame):
    """
    Базовый класс страницы.

    Пример:

        class Settings(Page):
            def setup(self):
                self.button('Скачать', self.download, size=(140, 40), pos=(20, 20))

            def download(self):
                print('Скачивание...')
    """

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app          # ссылка на главное приложение (App),
                                 # чтобы можно было переключать страницы
                                 # прямо из кнопок страницы (self.go_to(...))
        self.setup()

    def setup(self):
        """Переопределите этот метод и опишите тут виджеты страницы."""
        pass

    # ---------- Виджеты страницы ----------

    def button(self, text, command=None, size=(120, 30), pos=(0, 0), **kwargs):
        w = tk.Button(self, text=text, command=command, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def label(self, text, size=(120, 30), pos=(0, 0), **kwargs):
        w = tk.Label(self, text=text, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def entry(self, size=(120, 30), pos=(0, 0), **kwargs):
        w = tk.Entry(self, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def text(self, size=(200, 100), pos=(0, 0), **kwargs):
        w = tk.Text(self, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def checkbox(self, text, variable=None, size=(150, 25), pos=(0, 0), **kwargs):
        w = tk.Checkbutton(self, text=text, variable=variable, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def widget(self, widget_class, size=(120, 30), pos=(0, 0), **kwargs):
        """Универсальный способ добавить любой tkinter-виджет
        (Listbox, Scale, Radiobutton и т.д.), не описанный отдельным методом."""
        w = widget_class(self, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def go_to(self, page_name):
        """Возвращает функцию переключения на другую страницу —
        удобно передавать прямо в command= кнопки."""
        return lambda: self.app.show(page_name)


class App(tk.Tk):
    """
    Главное окно приложения.

    Пример:

        app = App(title='Пример', icon='пример.png', size=(800, 600))
        app.page_area(size=(760, 500), pos=(20, 60))   # область под страницы

        app.register(Main, 'main')
        app.register(Settings, 'settings')

        app.button('Настройки', app.go_to('settings'), size=(120, 30), pos=(20, 20))

        app.show('main')
        app.run()
    """

    def __init__(self, title='Приложение', icon=None, size=(800, 600)):
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self._icon_ref = None
        self._set_icon(icon)

        self._pages = {}
        self._current = None
        self._container = None
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ---------- Настройка окна ----------

    def _set_icon(self, icon_path):
        if not icon_path:
            return
        try:
            if icon_path.lower().endswith('.ico'):
                self.iconbitmap(icon_path)
            else:
                img = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, img)
                self._icon_ref = img  # хранится, чтобы картинку не убрал сборщик мусора
        except Exception as e:
            print(f'Не удалось установить иконку: {e}')

    # ---------- Виджеты главного окна (шапка/меню, общие для всех страниц) ----------

    def button(self, text, command=None, size=(120, 30), pos=(0, 0), **kwargs):
        w = tk.Button(self, text=text, command=command, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def label(self, text, size=(120, 30), pos=(0, 0), **kwargs):
        w = tk.Label(self, text=text, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    def widget(self, widget_class, size=(120, 30), pos=(0, 0), **kwargs):
        w = widget_class(self, **kwargs)
        w.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        return w

    # ---------- Область отображения страниц ----------

    def page_area(self, size=(600, 500), pos=(0, 50)):
        """Создаёт область, внутри которой будут показываться страницы."""
        container = tk.Frame(self)
        container.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
        self._container = container
        return container

    def register(self, page_class, name=None):
        """Создаёт страницу (класс, унаследованный от Page) и регистрирует её
        под именем name (по умолчанию — имя класса)."""
        if self._container is None:
            self.page_area()
        name = name or page_class.__name__
        page = page_class(self._container, self)
        page.place(x=0, y=0, relwidth=1, relheight=1)
        self._pages[name] = page
        if self._current is None:
            self._current = name
        else:
            page.place_forget()
        return page

    def show(self, name):
        """Показывает страницу с именем name, остальные скрывает."""
        if name not in self._pages:
            raise ValueError(f'Страница "{name}" не зарегистрирована')
        for pname, page in self._pages.items():
            if pname == name:
                page.place(x=0, y=0, relwidth=1, relheight=1)
                page.tkraise()
            else:
                page.place_forget()
        self._current = name

    def go_to(self, name):
        """Возвращает функцию переключения на страницу name —
        удобно передавать прямо в command= кнопки."""
        return lambda: self.show(name)

    def run(self):
        self.mainloop()
