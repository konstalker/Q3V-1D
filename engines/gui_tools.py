"""
gui_tools.py — общий PyQt6-фреймворк для GUI.
Импортируйте App / Page / RedirectToText / check_worker из этого модуля
в любом скрипте-точке входа — интерфейс будет одинаковым везде.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QTextEdit, QVBoxLayout
)
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QSize
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
    """Базовый класс страницы. Наследуйтесь и переопределяйте setup(),
    чтобы описать содержимое страницы."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.layout_ = QVBoxLayout()
        self.setLayout(self.layout_)
        self.setup()

    def setup(self):
        """Переопределяется в наследниках."""
        pass

    def text(self, size=(400, 300)):
        """Добавляет на страницу read-only текстовое поле (консоль)."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        widget.setFixedSize(QSize(*size))
        self.layout_.addWidget(widget)
        return widget


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
        self.window.resize(*size)

        self.stack = QStackedWidget()
        self.window.setCentralWidget(self.stack)

        self._pages = {}

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
