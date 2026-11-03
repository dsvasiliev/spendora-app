import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget

from entities.dto.release import Release
from infrastructure.tools.define_error import define_error


class LoadUpdateInfo(QThread):
    """Проверить на наличие обновлений"""
    finished = Signal(Release, Release)

    def __init__(self, actual_url: str, important_url: str, parent: QWidget) -> None:
        super().__init__(parent)
        self.actual_url = actual_url
        self.important_url = important_url

    def run(self):
        try:
            actual_response = requests.get(self.actual_url, timeout=5)
            actual_response.raise_for_status()
            actual_dict = actual_response.json()
            important_response = requests.get(self.important_url, timeout=5)
            important_response.raise_for_status()
            important_dict = important_response.json()
            self.finished.emit(Release.from_dict(actual_dict), Release.from_dict(important_dict))
        except requests.RequestException:
            define_error("Поиск обновления", "Не удалось подключится к серверу")
        # except (KeyError, ValueError) as e:
        #     define_error("Получение данных об обновлении", e)
