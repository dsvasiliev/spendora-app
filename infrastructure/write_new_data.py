from pathlib import Path

from PySide6.QtCore import Signal, QObject
from openpyxl.reader.excel import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from entities.dto.cateroty import Category
from entities.dto.product import Product


class WriteNewData(QObject):
    """Запись данных в таблицу"""
    progress_updated = Signal()

    # def __init__(
    #         self,
    #         table_name: str,
    #         month_index: int,
    #         products_and_categories: list[tuple[Product, Category]],
    # ):
    #     super().__init__()
    #     self.table_name = table_name
    #     self.month_index = month_index
    #     self.products_and_categories = products_and_categories

    def sync_start(
            self,
            table_path: Path,
            month_index: int,
            products_and_categories: list[tuple[Product, Category]]
    ):
        # print(self.table_name)
        work_book = load_workbook(table_path)
        month_sheet = work_book[work_book.sheetnames[month_index]]

        for product, category in products_and_categories:
            now_cell: dict[str, int] = {
                "row": -1,
                "column": -1
            }
            max_row = category.row + category.add_row
            for row in range(category.row, max_row + 1):
                for column in range(2, 15):
                    if month_sheet.cell(row=row, column=column).value is None:
                        now_cell["row"] = row
                        now_cell["column"] = column
                        break
                if now_cell["row"] != -1:
                    break
            # Если свободная ячейка так и не была найдена, добавляем к последней
            if now_cell["row"] < 1:
                now_cell["row"] = max_row
                now_cell["column"] = 14
                # Для оптимизации. Был ли уже текст в ячейке
                need_to_add = True
            else:
                need_to_add = False
            if product.count % 1 == 0:
                # Если продуктов счётное кол-во
                for i in range(int(product.count)):
                    write_table_value(month_sheet, now_cell, need_to_add, product.price)
                    # Поиск следующей свободной ячейки
                    if now_cell["column"] < 14:
                        now_cell["column"] += 1
                    else:
                        if now_cell["row"] != max_row:
                            now_cell["row"] += 1
                            now_cell["column"] = 2
                self.progress_updated.emit()
            else:
                # Если не счётное:
                write_table_value(month_sheet, now_cell, need_to_add, product.price * product.count)
                self.progress_updated.emit()

        try:
            work_book.save(table_path)
            work_book.close()
        except PermissionError as e:
            work_book.close()
            print("ОШИБКА (при записи в таблицу): " + str(e))
        except Exception as e:
            work_book.close()
            print("ОШИБКА (при сохранении в таблицу): " + str(e))


def write_table_value(
        sheet: Worksheet,
        cell: dict[str, int],
        need_to_add: bool,
        value: float | int
) -> None:
    """Записать значение в таблицу"""
    if need_to_add:
        cell_value = sheet.cell(row=cell["row"], column=cell["column"]).value
        if isinstance(cell_value, (int, float)):
            old_value = cell_value
        else:
            old_value = 0
        try:
            sheet.cell(
                row=cell["row"],
                column=cell["column"],
                value=old_value + value
            )
        except ValueError as e:
            print("ОШИБКА (при записи в таблицу): " + str(e))

    else:
        try:
            sheet.cell(
                row=cell["row"],
                column=cell["column"],
                value=value
            )
        except ValueError as e:
            print("ОШИБКА (при записи в таблицу): " + str(e))
