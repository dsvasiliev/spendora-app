from PySide6.QtCore import Signal, QObject

from models.groups_model import GroupsModel
from models.month_model import MonthModel
from infrastructure.parser_router import ParserRouter
from models.categories_model import CategoriesModel
from models.products_model import ProductsModel
from models.receipts_model import ReceiptsModel
from models.settings_model import SettingsModel
from models.table_model import TableModel
from services.db_clean_service import DBCleanService
from services.making_result_service import MakingResultService
from services.read_receipts_service import ReadReceiptsService
from services.return_servise import ReturnService
from services.select_categories_service import SelectCategoriesService


class AppContext(QObject):
    """Контекст всего приложения, содержащий ссылки на модели и сервисы"""
    file_parsed = Signal(int)
    parsing_end = Signal()
    file_is_writing = Signal()
    file_writing_end = Signal()

    def __init__(self):
        super().__init__()

        # Модели
        self.table_model = TableModel()
        self.receipts_model = ReceiptsModel()
        self.month_model = MonthModel()
        self.products_model = ProductsModel()
        self.categories_model = CategoriesModel()
        self.groups_model = GroupsModel()
        self.settings_model = SettingsModel()

        # Инфраструктура
        self.parser_router = ParserRouter()

        # Сервисы
        self.read_receipts_service = ReadReceiptsService(
            self.receipts_model,
            self.table_model,
            self.products_model,
            self.categories_model,
            self.groups_model,
            self.parser_router,
        )
        self.making_result_service = MakingResultService(
            self.table_model,
            self.month_model,
            self.products_model,
            self.categories_model
        )
        self.return_service = ReturnService(
            self.receipts_model,
            self.products_model,
        )
        self.select_categories_service = SelectCategoriesService(
            self.products_model,
            self.categories_model,
        )
        self.db_clean_service = DBCleanService()
        #
        #
        #
        #
        #
        #
        # # self._need_to_parse_table: bool = True
        #
        # # self.db_manager = DBManager(DB_PATH)
        # self.category_storage = CategoriesModel()
        # self.products_storage = ProductsModel()
        # # self.async_parser = Parse(self)
        # # self.async_parser.progress_updated.connect(self.file_parsed.emit)
        # # self.async_parser.parsing_end.connect(self.parsing_end.emit)
        #
        # self.table_writer = None
        # self.table_reader = None
        # self.last_month_total: float | None = None
        #
        # self.table_name: str = ""
        # self.file_names: list[str] = []
        # self.now_month_index: int = datetime.now().month - 1
        #
        # # self.update_url = ""
        #
        # # self.parser_model = ParserRouter()
        #
        # self.settings_model = SettingsModel()

    # def write_func(self):
    #     self.table_writer = WriteNewData(
    #         self.table_name,
    #         self.now_month_index,
    #         # Массив вида (Объект продукта, Объект его категории)
    #         [(product, self.category_storage.get_by_id(product.category_id)) for product in
    #          self.products_storage.get_all()]
    #     )
    #     self.table_writer.progress_updated.connect(self.file_is_writing.emit)
    #     self.table_writer.parsing_end.connect(self._table_wrote)
    #     self.table_writer.start()

    # def cleanup_old_data(self):
    #     """Очистка старых данных из БД"""
    #     self.db_manager.cleanup_old_data()

    # def parse(self):
    #     self.async_parser.start()

    # def get_all_groups(self) -> list[Group]:
    #     """Получение всех групп"""
    #     return self.category_storage.get_groups()

    # def get_category_name(self, category_id: int) -> str:
    #     """Получить название категории по ID"""
    #     if category_id < 0:
    #         return ""
    #     return self.category_storage.get_title_by_id(category_id)

    # def set_new_category(self, product_id: int, category_id: int):
    #     """Установить новую категорию"""
    #     self.products_storage.set_category(product_id, category_id)
    #     self.db_manager.set_category(
    #         self.products_storage.get_by_id(product_id).name,
    #         self.category_storage.get_by_id(category_id).name
    #     )

    # def get_product(self, product_id: int) -> Product:
    #     """Получить продукт по id"""
    #     return self.products_storage.get_by_id(product_id)

    # def get_all_products(self) -> list[Product]:
    #     """Получить все продукты"""
    #     return self.products_storage.get_all()

    # def _table_wrote(self):
    #     self.table_reader = OldDataReader(self.table_name, self.now_month_index, self.category_storage.get_all())
    #     self.table_reader.process_end.connect(self._end_writing)
    #     try:
    #         self.table_reader.start()
    #     except PermissionError:
    #         print("...")
    #     except Exception as e:
    #         print(e)

    # def _end_writing(self, amount: int):
    #     self.last_month_total = amount
    #     self.file_is_writing.emit()
    #     self.file_writing_end.emit()

    # def now_month_total_cost(self):
    #     return self.products_storage.get_total_cost()
    #
    # def previous_month_total_cost(self):
    #     return self.last_month_total

    # def make_forecast(self) -> int | None:
    #     """Прогноз на следующий месяц"""
    #     if self.last_month_total == 0:
    #         return None
    #     now_month_total = self.products_storage.get_total_cost()
    #     pers = now_month_total / (self.last_month_total / 100)
    #     return round(now_month_total * pers / 100)

    # def set_month(self, month_id: int) -> None:
    #     """Установить месяц для анализа"""
    #     self.now_month_index = month_id

    # def close_app(self):
    #     """Закрытие приложения"""
    #     self.db_manager.close()


# class Parse(QThread):
#     progress_updated = Signal(int)
#     parsing_end = Signal()
#
#     def __init__(self, model: AppContext):
#         super().__init__()
#         self.model = model
#
#     def run(self):
#         count = 0
#         for index in range(count(self.model.file_names)):
#             # sleep(1)
#             self.model.parser_model.parsers_router(self.model.file_names[index], self.model.products_storage)
#             count += 1
#             self.progress_updated.emit(count)
#         self.model.category_storage.parse_table(self.model.table_name)
#         count += 1
#         self.progress_updated.emit(count)
#         self.model.products_storage.find_category_for_all(self.model.category_storage, DBManager(DB_PATH))
#         count += 1
#         self.progress_updated.emit(count)
#         self.parsing_end.emit()

# MODEL.now_month_index = 1
# MODEL.table_name = "D:\\Spendora\\Project\\for_tests\\Расходы за 20...г..xlsx"
# table_writer = TableReader(MODEL)
# table_writer.process_end.connect(print)
# table_writer.run()
