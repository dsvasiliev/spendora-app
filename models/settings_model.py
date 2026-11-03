from PySide6.QtCore import QObject, QSettings

from infrastructure.network.send_statistic import SendStatistic


class SettingsModel(QObject):
    def __init__(self):
        super().__init__()
        self.storage = QSettings("Spendora", "Spendora App")
        self.sender: SendStatistic | None = None

    def check_if_back(self):
        """Если пользователь вернулся в приложение, отправляем статистику"""
        status = self.storage.value("is_user_back", 0)
        if status == 0:
            self.storage.setValue("is_user_back", 1)
        elif status == 1:
            sender = SendStatistic('back')
            sender.status_changed.connect(self.statistic_send)
            sender.start()
        else:
            self.storage.setValue("is_user_back", 2)

    def statistic_send(self, status: bool) -> None:
        """После отправки статистики можно перезаписать значение"""
        if status:
            self.storage.setValue("is_user_back", 2)