from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtSvgWidgets import QSvgWidget

from infrastructure.tools.define_error import define_error

ROOT_DIR = Path(__file__).cwd()

def get_path(*steps: str) -> Path:
    """Получить путь до файла"""
    path = ROOT_DIR
    for step in steps:
        path = path.joinpath(step)
    return path

MAIN_STYLES = get_path("ui", "src", "styles", "main_window.qss")

def get_icon(*steps: str) -> QIcon:
    """Получить элемент QIcon"""
    icon_p = get_path("ui", "src", "icons", *steps)
    if icon_p.exists():
        return QIcon(str(icon_p))
    else:
        define_error("загрузка иконки QICon", f"файл не найден {icon_p}")
        return QIcon()


def get_svg_widget(*steps: str) -> QSvgWidget:
    """Получить элемент QSvgWidget"""
    icon_p = get_path("ui", "src", "icons", *steps)
    if icon_p.exists():
        return QSvgWidget(str(icon_p))
    else:
        define_error("загрузка иконки QSvgWidget", "файл не найден")
        return QSvgWidget()