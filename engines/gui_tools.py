"""
gui_tools.py — общий PyQt6-фреймворк для GUI.
Импортируйте App / Page / RedirectToText / check_worker из этого модуля
в любом скрипте-точке входа — интерфейс будет одинаковым везде.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QSize, Qt
from PyQt6.QtGui import QIcon, QTextCursor


class RedirectToText(QObject):
    """Файлоподобный объект: write()/flush() как у sys.stdout,
    но текст уходит в QTextEdit. Потокобезопасно — используется сигнал,
    поэтому можно печатать из фонового потока без риска падения GUI."""

    _text_written = pyqtSignal(str)

    def __init__(self, text_widget: QTextEdit):
        super().__init__()
        self.text_widget = text_widget
        self._text_written.connect(self._append)

    def write(self, text):
        self._text_written.emit(str(text))

    def flush(self):
        pass

    def _append(self, text):
        cursor = self.text_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.text_widget.setTextCursor(cursor)
        self.text_widget.ensureCursorVisible()


class Page(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.layout_ = QVBoxLayout()
        self.layout_.setContentsMargins(0, 0, 0, 0)  # убрать отступы от краёв
        self.layout_.setSpacing(0)                   # убрать интервалы между виджетами
        self.setLayout(self.layout_)
        self.setup()

    def setup(self):
        pass

    def _place(self, target_layout, widget, index=None, alignment=None):
        """Общая логика добавления виджета в layout: в конец, в конкретную
        позицию (index) и/или с выравниванием (alignment)."""
        kwargs = {} if alignment is None else {'alignment': alignment}
        if index is None:
            target_layout.addWidget(widget, **kwargs)
        else:
            target_layout.insertWidget(index, widget, **kwargs)

    def text(self, size=(400, 300), layout=None, index=None, alignment=None):
        widget = QTextEdit()
        widget.setReadOnly(True)
        widget.setFixedSize(QSize(*size))
        self._place(layout or self.layout_, widget, index=index, alignment=alignment)
        return widget

    def button(self, label, callback=None, size=(400, 40), visible=True, enabled=True,
               layout=None, index=None, alignment=None):
        """Кнопка с тем же паттерном, что и text(): создаётся, сразу
        добавляется в layout страницы и возвращается наружу, чтобы
        вызывающий код мог её показывать/прятать/включать по своей логике.

        layout — если нужно поместить кнопку не в основной вертикальный
        layout страницы, а, например, в ряд, созданный через row().
        index — позиция внутри layout (0 = в начало), по умолчанию — в конец.
        alignment — Qt.AlignmentFlag.AlignHCenter/AlignLeft/AlignRight и т.п.,
        актуально когда виджет уже, чем страница/ряд."""
        widget = QPushButton(label)
        widget.setFixedSize(QSize(*size))
        widget.setVisible(visible)
        widget.setEnabled(enabled)
        if callback is not None:
            widget.clicked.connect(callback)
        self._place(layout or self.layout_, widget, index=index, alignment=alignment)
        return widget

    def row(self, spacing=None, margins=None, index=None):
        """Создаёт горизонтальный QHBoxLayout, кладёт его в основной layout
        страницы и возвращает — передавайте его как layout=... в text()/
        button(), чтобы расположить несколько виджетов в один ряд:

            row = self.row(spacing=8)
            self.button('Да', layout=row, size=(190, 40))
            self.button('Нет', layout=row, size=(190, 40))
        """
        row_layout = QHBoxLayout()
        if spacing is not None:
            row_layout.setSpacing(spacing)
        if margins is not None:
            row_layout.setContentsMargins(*margins)
        if index is None:
            self.layout_.addLayout(row_layout)
        else:
            self.layout_.insertLayout(index, row_layout)
        return row_layout

    def stretch(self, layout=None):
        """Добавляет растягивающийся пустой промежуток — раздвигает
        соседние виджеты к краям (например, прижимает кнопку к низу
        страницы, если вызвать stretch() перед её добавлением)."""
        (layout or self.layout_).addStretch()

    def spacing(self, px):
        """Промежуток между виджетами в основном layout страницы."""
        self.layout_.setSpacing(px)

    def margins(self, left, top, right, bottom):
        """Отступы всего layout страницы от краёв окна."""
        self.layout_.setContentsMargins(left, top, right, bottom)


class App:
    """Обёртка над QApplication + QMainWindow со стеком страниц.
    Создаётся один раз в точке входа, но сам класс живёт здесь,
    так что все точки входа получают идентичный интерфейс."""

    def __init__(self, title='App', icon=None, size=(800, 600)):
        self.qapp = QApplication.instance() or QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(title)
        if icon:
            self.window.setWindowIcon(QIcon(icon))
        self.window.setFixedSize(QSize(*size))

        self.stack = QStackedWidget()
        self.window.setCentralWidget(self.stack)

        self._pages = {}

        screen = self.qapp.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.window.frameGeometry()

        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.window.move(window_geometry.topLeft())

    def page_area(self, size=(800, 600), pos=(0, 0)):
        """Оставлено для совместимости с оригинальным API —
        задаёт размер и позицию окна."""
        self.window.resize(*size)
        self.window.move(*pos)

    def register(self, page_cls, name):
        """Создаёт экземпляр страницы и добавляет в стек."""
        page = page_cls(self)
        self._pages[name] = page
        self.stack.addWidget(page)
        if self.stack.count() == 1:
            self.stack.setCurrentWidget(page)
        return page

    def show_page(self, name):
        self.stack.setCurrentWidget(self._pages[name])

    def run(self):
        self.window.show()
        return self.qapp.exec()


def check_worker(app, thread, interval_ms, exit_func):
    """Периодически проверяет, жив ли фоновый поток (через QTimer,
    не блокируя event loop). Когда поток завершился — вызывает exit_func()."""
    timer = QTimer()

    def _check():
        if not thread.is_alive():
            timer.stop()
            exit_func()

    timer.timeout.connect(_check)
    timer.start(interval_ms)
    app._worker_timer = timer  # держим ссылку, чтобы таймер не убрал GC
    return timer

class RedirectToText(QObject):
    """Файлоподобный объект: write()/flush() как у sys.stdout,
    но текст уходит в QTextEdit. Потокобезопасно — через сигнал.
    Поддерживает \\r (перезапись текущей строки) и \\n."""

    _text_written = pyqtSignal(str)

    def __init__(self, text_widget: QTextEdit):
        super().__init__()
        self.text_widget = text_widget
        self._text_written.connect(self._append)

    def write(self, text):
        self._text_written.emit(str(text))

    def flush(self):
        pass

    def _append(self, text):
        text = text.replace('\r\n', '\n')

        cursor = self.text_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        while '\r' in text:
            before, text = text.split('\r', 1)
            if before:
                cursor.insertText(before)

            # выделяем от текущей позиции до начала строки и удаляем —
            # это "перезаписывает" текущую строку, как в терминале
            cursor.movePosition(
                QTextCursor.MoveOperation.StartOfLine,
                QTextCursor.MoveMode.KeepAnchor
            )
            cursor.removeSelectedText()

        if text:
            cursor.insertText(text)

        self.text_widget.setTextCursor(cursor)
        self.text_widget.ensureCursorVisible()
