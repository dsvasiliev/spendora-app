from PySide6.QtCore import QObject, Signal

from infrastructure.network.send_statistic import SendStatistic
from models.products_model import ProductsModel
from models.receipts_model import ReceiptsModel


class ReturnService(QObject):
    """Сервис для возвращения к начальной странице"""
    start_process = Signal()
    process_finished = Signal()

    def __init__(
            self,
            receipts_model: ReceiptsModel,
            products_model: ProductsModel,
    ):
        super().__init__()
        self.receipts_model = receipts_model
        self.products_model = products_model
        self.statistic_worker = SendStatistic('continue')
        self.statistic_worker.finished.connect(self.process_finished)

    def sync_start(self):
        self.start_process.emit()
        self.receipts_model.reset()
        self.products_model.reset()
        self.statistic_worker.start()
