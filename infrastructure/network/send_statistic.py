import requests
from PySide6.QtCore import QThread, Signal

from config import STATISTIC_URL, VERSION
from infrastructure.tools.define_error import define_error


class SendStatistic(QThread):
    """Отправить на сервер статистику по приложению"""
    status_changed = Signal(bool)

    def __init__(self, statistic_type: str) -> None:
        super().__init__()
        self.statistic_type = statistic_type

    def run(self):
        try:
            requests.get(f"{STATISTIC_URL}/{self.statistic_type}/{VERSION}", timeout=5)
            self.status_changed.emit(True)
        except requests.RequestException:
            define_error("Отправка статистики", "Не удалось подключится к серверу")
            self.status_changed.emit(False)
        except (KeyError, ValueError) as e:
            define_error("Отправка статистики", e)
            self.status_changed.emit(False)

# def send_statistic(statistic_type: str) -> None:
#     """Отправить на сервер статистику по приложению"""
#     try:
#         worker = SendStatistic(statistic_type)
#         worker.start()
#     except Exception as e:
#         print(e)
