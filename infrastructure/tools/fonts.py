from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication

from infrastructure.tools.define_error import define_error


def load_fonts(
        app: QApplication,
        font_link: str,
) -> None:
    """Установить шрифт для виджета"""
    font_id = QFontDatabase.addApplicationFont(font_link)
    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            app.setFont(QFont(families[0], 10))
            return
    define_error("Загрузка шрифтов", "Не удалось загрузить шрифт")
