from PySide6.QtCore import Signal, QThread

from config import DB_PATH
from entities.dto.product import DetectionType
from entities.errors.parsing_error import ParsingError
from infrastructure.read_categories import read_categories
from infrastructure.db_manager import DBManager
from infrastructure.parser_router import ParserRouter
from models.categories_model import CategoriesModel
from models.groups_model import GroupsModel
from models.products_model import ProductsModel
from models.receipts_model import ReceiptsModel
from models.table_model import TableModel


class ReadReceiptsService(QThread):
    """Обработка выбранных чеков и таблицы"""
    send_total = Signal(int)
    progress = Signal(int)
    start_process = Signal()
    finish_process = Signal()
    error = Signal(str)

    def __init__(
            self,
            receipts_model: ReceiptsModel,
            table_model: TableModel,
            products_model: ProductsModel,
            categories_model: CategoriesModel,
            groups_model: GroupsModel,
            parsers_router: ParserRouter,
    ):
        super().__init__()
        self.receipts_model = receipts_model
        self.table_model = table_model
        self.products_model = products_model
        self.categories_model = categories_model
        self.groups_model = groups_model
        self.parsers_router = parsers_router

    def run(self):
        self.send_total.emit(self.receipts_model.get_receipts_count() + 2)
        self.start_process.emit()
        count = 0
        for receipt_path in self.receipts_model.get_receipts_paths():
            try:
                new_products = self.parsers_router.parsers_router(receipt_path)
                self.products_model.add_list(new_products)
            except ParsingError:
                self.error.emit(str(receipt_path))

            count += 1
            self.progress.emit(count)
        if self.table_model.get_path() != self.categories_model.for_table:
            categories, groups = read_categories(self.table_model.get_path())
            self.categories_model.reset()
            self.categories_model.set(categories, self.table_model.get_path())
            self.groups_model.reset()
            self.groups_model.set(groups)
        count += 1
        self.progress.emit(count)
        self.find_category_for_all()
        count += 1
        self.progress.emit(count)
        self.finish_process.emit()

    def find_category_for_all(self):
        """Постараться распределить категории автоматически"""
        db_manager = DBManager(DB_PATH)
        all_products = self.products_model.get_all()
        for product_id in range(len(all_products)):
            category_name = db_manager.get_category_name(all_products[product_id].name)
            if category_name is not None:
                new_category_id = self.categories_model.find_by_name(category_name)
                if new_category_id > 0:
                    self.products_model.set_category(
                        product_id,
                        new_category_id,
                        DetectionType.FROM_DB
                    )
                    continue
            category_by_textmatch = self.categories_model.find_match(all_products[product_id].name)
            if category_by_textmatch > 0:
                self.products_model.set_category(
                    product_id,
                    category_by_textmatch,
                    DetectionType.DETECTED
                )
        db_manager.close()
