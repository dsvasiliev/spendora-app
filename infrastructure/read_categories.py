from pathlib import Path

from openpyxl import load_workbook

from entities.dto.cateroty import Category
from entities.dto.group import Group


def read_categories(table_path: Path) -> tuple[list[Category], list[Group]]:
    """Чтение категорий из таблицы"""
    categories: list[Category] = []
    groups: list[Group] = []
    # Отвечает за последнюю группу в списке. Если категории идут вне группы, то равен -1
    last_category_index = -1
    free_rows = 0
    # При создании категория становится открытой. Далее надо определить, когда начинается другая
    last_opened_category = -1

    work_book = load_workbook(table_path)
    one_month = work_book[work_book.sheetnames[0]]

    # Выделяем строки, где есть широкие заголовки
    headers_rows = [merge_cell.min_row for merge_cell in one_month.merged_cells if
                    merge_cell.min_col != merge_cell.max_col]

    # Перебираем все строки
    for cell in one_month['A'][1:]:
        # Если клетка ограничена линией, то закрываем незаконченную категорию
        if cell.border.top.border_style or cell.value:
            if last_opened_category != -1:
                categories[last_opened_category].add_row = free_rows
                last_opened_category = -1
            free_rows = 0

        if cell.row in headers_rows:
            # Надо получить название. Оно хранится в первой клетке группы
            for column_name in ['A', 'B', 'C', 'D', 'E', 'F']:
                header_cell = one_month[f'{column_name}{cell.row}']
                if header_cell.value is not None:
                    if not header_cell.font.italic:
                        last_category_index = len(groups)
                        groups.append(Group(
                            header_cell.value,
                            []
                        ))
                    else:
                        last_category_index = -1
        elif cell.value:
            if not cell.font.italic:
                categories.append(Category(
                    len(categories),
                    cell.value,
                    cell.row,
                    0
                ))
                new_category_id = len(categories) - 1
                last_opened_category = new_category_id  # Новая категория не закончена
                # Добавляем категорию в группу
                if last_category_index != -1:
                    groups[last_category_index].categories_id.append(new_category_id)
        else:
            free_rows += 1

        # Скорее всего, началось пустое пространство
        if free_rows > 10:
            break
    return categories, groups
