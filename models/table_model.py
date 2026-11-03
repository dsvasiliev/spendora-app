from pathlib import Path

from PySide6.QtCore import QObject


class TableModel(QObject):
    """Модель таблицы"""
    def __init__(self):
        super().__init__()
        self.__table_path: Path = Path()

    def get_path(self) -> Path:
        return self.__table_path

    def get_name(self) -> str:
        return self.__table_path.name

    def set_path(self, table_path):
        self.__table_path = Path(table_path).resolve()

    def reset(self):
        self.__table_path = Path()