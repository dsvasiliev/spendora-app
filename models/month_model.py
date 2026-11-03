from datetime import datetime

from PySide6.QtCore import QObject


class MonthModel(QObject):
    def __init__(self):
        super().__init__()
        self.__month_index: int = datetime.now().month - 1

    def get_month_index(self) -> int:
        return self.__month_index

    def set_month_index(self, month_index: int) -> None:
        self.__month_index = month_index