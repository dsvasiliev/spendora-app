from PySide6.QtCore import QObject

from config import DB_PATH
from entities.dto.product import DetectionType
from infrastructure.db_manager import DBManager
from models.categories_model import CategoriesModel
from models.products_model import ProductsModel


class SelectCategoriesService(QObject):
    def __init__(
            self,
            products_model: ProductsModel,
            categories_model: CategoriesModel,
    ):
        self.products_model = products_model
        self.categories_model = categories_model
        super().__init__()

    def set_category(self, product_id: int, new_category_id: int, detection_type: DetectionType) -> None:
        """Установка новой категории"""
        self.products_model.set_category(product_id, new_category_id, detection_type)
        db_manager = DBManager(DB_PATH)
        db_manager.set_category(
            self.products_model.get_by_id(product_id).name,
            self.categories_model.get_by_id(new_category_id).name
        )
        db_manager.close()
