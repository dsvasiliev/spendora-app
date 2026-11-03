from pathlib import Path

from openpyxl.reader.excel import load_workbook

from entities.dto.cateroty import Category


def read_old_data(
        table_path: Path,
        month_index: int,
        all_categories: list[Category]
) -> float:
    """Считываем расходы за предыдущий месяц"""
    work_book = load_workbook(table_path)
    if month_index == 0:
        return 0
    month_sheet = work_book[work_book.sheetnames[month_index - 1]]
    summ = 0
    for category in all_categories:
        for row in range(category.row, category.row + category.add_row + 1):
            for column in range(2, 15):
                cell_value = month_sheet.cell(row=row, column=column).value
                if isinstance(cell_value, (int, float)):
                    summ += cell_value
                elif cell_value is None:
                    break
    work_book.close()
    return summ
