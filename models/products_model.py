from PySide6.QtCore import QObject, Signal

from entities.dto.product import Product, DetectionType


class ProductsModel(QObject):
    attention_count_change = Signal()

    def __init__(self):
        super().__init__()
        self._products: dict[int, Product] = {}
        self._data_to_id: dict[tuple[str, float], int] = {}
        self._next_id = 0
        self._attention_count = 0

    def reset(self):
        self._products.clear()
        self._data_to_id.clear()
        self._next_id = 0
        self._attention_count = 0

    def add_list(self, products_list: list[Product]):
        """Добавить несколько продуктов"""
        for product in products_list:
            self.add(product)

    def add(self, product: Product):
        main_data = (product.name, product.price)
        if main_data in self._data_to_id:
            old_id = self._data_to_id[main_data]
            self._products[old_id].count += product.count
            self._products[old_id].files.append(product.files[0])
        else:
            self._products[self._next_id] = Product(
                self._next_id,
                product.name,
                product.price,
                product.count,
                product.files,
                -1,
                DetectionType.UNKNOWN
            )
            self._next_id += 1
            self._attention_count += 1
            self._data_to_id[main_data] = self._next_id

    def set_category(self, product_id: int, category_id: int, detection_type: DetectionType):
        """Установить новое значение для поля 'Категория'"""
        if self._products[product_id].category_id == -1:
            self._attention_count -= 1
            self.attention_count_change.emit()
        self._products[product_id].category_id = category_id
        self._products[product_id].detection_type = detection_type

    def get_attention_count(self) -> int:
        return self._attention_count

    def get_by_id(self, product_id: int) -> Product:
        return self._products[product_id]

    def get_all(self) -> list[Product]:
        """Список всех продуктов"""
        return list(self._products.values())

    def get_total_cost(self) -> float:
        """Итоговая стоимость всех продуктов"""
        return sum(product.count * product.price for product in self._products.values())

    def get_recognized_products(self) -> list[Product]:
        """Получить продукты по типу автоматического распознавания"""
        return [product for product in self._products.values() if product.detection_type == DetectionType.FROM_DB]

    def get_attention_products(self) -> list[Product]:
        """Получить продукты по типу автоматического распознавания"""
        return [product for product in self._products.values() if product.detection_type != DetectionType.FROM_DB]

    def count(self):
        return len(self._products)

    def delete_product(self, product_id: int):
        """Удалить продукт"""
        if self._products[product_id].category_id == -1:
            self._attention_count -= 1
            self.attention_count_change.emit()
        self._products.pop(product_id)

    def __str__(self):
        return str(self._products)

#
# class TestProductsModel(ProductsModel):
#     def __init__(self):
#         super().__init__()
#         self.products = [
#             Product(
#                 0,
#                 "Продукт 1",
#                 45.6,
#                 4,
#                 ["file.eml"],
#                 1,
#                 DetectionType.UNKNOWN
#             ),
#             Product(
#                 1,
#                 "Продукт 2",
#                 25.6,
#                 2,
#                 ["file2.eml"],
#                 0,
#                 DetectionType.DETECTED
#             ),
#             Product(
#                 2,
#                 "Продукт 3",
#                 25.6,
#                 2,
#                 ["file2.eml"],
#                 2,
#                 DetectionType.FROM_DB
#             )
#         ]
#
#     def get_by_id(self, product_id: int) -> Product:
#         return self.products[product_id]
#
#     def get_all(self) -> list[Product]:
#         return self.products
#
#     def set_category(self, product_id: int, category_id: int):
#         pass
#
#     def get_total_cost(self) -> float:
#         """Итоговая стоимость всех продуктов"""
#         return 45
