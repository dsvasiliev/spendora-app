from PySide6.QtWidgets import QWidget
from hPyT import title_bar_color

from infrastructure.tools.define_error import define_error
from infrastructure.tools.files import get_path


def set_header_color(widget: QWidget):
    """Установка цвета заголовка"""
    title_bar_color.set(widget, "#F4F1EC")


def load_styles(widget: QWidget, *files: str):
    """Установить стили из файлов в папке styles"""
    style_text = ""
    for file in files:
        qss_path = get_path("ui", "src", "styles", file)
        if qss_path.exists():
            style_text += qss_path.read_text(encoding="utf-8")
        else:
            define_error("Загрузка стилей", "Не удалось загрузить стили")
    widget.setStyleSheet(style_text)