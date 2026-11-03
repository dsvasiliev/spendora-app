from PySide6.QtCore import QThread

from config import DB_PATH
from infrastructure.db_manager import DBManager


class DBCleanService(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        db_manager = DBManager(DB_PATH)
        db_manager.cleanup_old_data()
