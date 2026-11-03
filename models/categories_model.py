from pathlib import Path

from entities.dto.cateroty import Category
from entities.dto.group import Group

# COLUMNS_NAMES = ['A', 'B', 'C', 'D', 'E', 'F']


class CategoriesModel:
    def __init__(self):
        self.__categories: list[Category] = []
        self.for_table: Path = Path()

    def reset(self):
        self.__categories.clear()

    # def parse_table(self, file_path: str):
    #     """Чтение категорий из таблицы"""
    #     if file_path == self._file_path:
    #         return
    #     self.reset()
    #     # Отвечает за последнюю группу в списке. Если категории идут вне группы, то равен -1
    #     last_category_index = -1
    #     free_rows = 0
    #     # При создании категория становится открытой. Далее надо определить, когда начинается другая
    #     last_opened_category = -1
    #
    #     work_book = load_workbook(file_path)
    #     one_month = work_book[work_book.sheetnames[0]]
    #
    #     # Выделяем строки, где есть широкие заголовки
    #     headers_rows = [merge_cell.min_row for merge_cell in one_month.merged_cells if
    #                     merge_cell.min_col != merge_cell.max_col]
    #
    #     # Перебираем все строки
    #     for cell in one_month['A'][1:]:
    #         # Если клетка ограничена линией, то закрываем незаконченную категорию
    #         if cell.border.top.border_style or cell.value:
    #             if last_opened_category != -1:
    #                 self._categories_add_rows[last_opened_category] = free_rows
    #                 last_opened_category = -1
    #             free_rows = 0
    #
    #         if cell.row in headers_rows:
    #             # Надо получить название. Оно хранится в первой клетке группы
    #             for column_name in COLUMNS_NAMES:
    #                 header_cell = one_month[f'{column_name}{cell.row}']
    #                 if header_cell.value is not None:
    #                     if not header_cell.font.italic:
    #                         last_category_index = count(self._groups)
    #                         self._groups.append(Group(
    #                             header_cell.value,
    #                             []
    #                         ))
    #                     else:
    #                         last_category_index = -1
    #         elif cell.value:
    #             if not cell.font.italic:
    #                 self._categories_titles.append(cell.value)
    #                 self._categories_rows.append(cell.row)
    #                 self._categories_add_rows.append(0)
    #                 new_category_id = count(self._categories_titles) - 1
    #                 last_opened_category = new_category_id  # Новая категория не закончена
    #                 # Добавляем категорию в группу
    #                 if last_category_index != -1:
    #                     self._groups[last_category_index].categories_id.append(new_category_id)
    #         else:
    #             free_rows += 1
    #
    #         # Скорее всего, началось пустое пространство
    #         if free_rows > 10:
    #             break
    def set(self, categories: list[Category], for_table: Path):
        self.__categories = categories
        self.for_table = for_table

    def get_by_id(self, category_id: int) -> Category:
        """Получение категории по id"""
        return self.__categories[category_id]

    def get_all(self) -> list[Category]:
        """Получить все категории"""
        return self.__categories

    def get_title_by_id(self, category_id: int) -> str:
        """Получить имя категории по id"""
        if category_id < 0:
            return ""
        return self.__categories[category_id].name

    def find_match(self, title: str) -> int:
        """Найти совпадение в названии с категорией"""
        for index in range(len(self.__categories)):
            if self.__categories[index].name in title:
                return index
        return -1

    def find_by_name(self, name: str) -> int:
        """Получаем индекс по названию категории"""
        for index in range(len(self.__categories)):
            if self.__categories[index].name == name:
                return index
        return -1


class TestCategoriesModel(CategoriesModel):
    def __init__(self):
        super().__init__()
        self.categories_titles = ["Кварт плата", "ОТ и ГВ", "Моб. Телефоны"]
        self.categories_rows: list[int] = [6, 8, 18]
        self.categories_add_rows: list[int] = [1, 1, 0]
        self.groups: list[Group] = [Group("Группа 1", [0, 1]), Group("Группа 2", [2])]

    def get_groups(self) -> list[Group]:
        return self.groups

    def get_title_by_id(self, category_id: int) -> str:
        """Получить имя категории по id"""
        return self.categories_titles[category_id]

    def get_by_id(self, category_id: int) -> Category:
        return Category(
            category_id,
            self.categories_titles[category_id],
            self.categories_rows[category_id],
            self.categories_add_rows[category_id]
        )

    def get_all(self) -> list[Category]:
        res = []
        for index in range(len(self.categories_titles)):
            res.append(Category(
                index,
                self.categories_titles[index],
                self.categories_rows[index],
                self.categories_add_rows[index]
            ))
        return res

# category_storage = CategoryStorage()
# category_storage.parse_table("../for_tests/Расходы за 20...г..xlsx")

# print(category_storage.get_by_id(0))
# print(category_storage.get_by_id(1))
# print(category_storage.get_by_id(2))
# print(category_storage.get_by_id(3))

# def get_categories(table_name: str) -> tuple[list[Category], list[Group]]:
#     categories: list[Category] = []
#     groups: list[Group] = []
#
#
#     return categories, groups


# categories, groups = get_categories("../for_tests/Расходы за 20...г..xlsx")
# print(categories)
# print(groups)
