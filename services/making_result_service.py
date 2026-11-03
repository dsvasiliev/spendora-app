from PySide6.QtCore import QThread, Signal

from entities.dto.dynamic import Dynamic
from infrastructure.read_old_data import read_old_data
from infrastructure.tools.text import format_number
from infrastructure.write_new_data import WriteNewData
from models.categories_model import CategoriesModel
from models.month_model import MonthModel
from models.products_model import ProductsModel
from models.table_model import TableModel


def make_forecast(
        previous_month_summ: float,
        now_month_summ: float,
) -> str:
    """Делаем сравнение с предыдущим месяцем"""
    if previous_month_summ == 0:
        return "К сожалению, недостаточно данных для формирования прогноза"
    pers = now_month_summ / (previous_month_summ / 100)
    return f'Если траты не изменятся, вы потратите <span style="font-weight:600;">{format_number(round(now_month_summ * pers / 100))} ₽</span>'


def make_comparison(
        previous_month_summ: float,
        now_month_summ: float
) -> tuple[Dynamic, str]:
    """На основе сравнения прогнозируем будущее расходы"""
    # self.amount.setText(f"{format_number(round(total_amount, 2))} ₽")
    if previous_month_summ == 0:
        return Dynamic.NONE, ""
    else:
        # self.trend_widget.setVisible(True)
        percents = round(now_month_summ / (previous_month_summ / 100))
        if percents > 100:
            # self.trend_icon.setPixmap(get_icon("Trending_up.svg").pixmap(20, 20))
            return Dynamic.NEGATIVE, f"На {percents - 100}% больше, чем в прошлом месяце"
        elif percents < 100:
            # self.trend_icon.setPixmap(get_icon("Trending_down.svg").pixmap(20, 20))
            # self.trend_text.setText(
            #     f'На {100 - percents}% меньше, чем в прошлом месяце. <span style="font-weight:700;">Так держать!</span>'
            # )
            return Dynamic.POSITIVE, f'На {100 - percents}% меньше, чем в прошлом месяце. <span style="font-weight:700;">Так держать!</span>'
        else:
            # self.trend_icon.setPixmap(get_icon("No_trending.svg").pixmap(20, 20))
            # self.trend_text.setText("В этом месяце Вы потратили примерно столько же, сколько в предыдущем")
            return Dynamic.NONE, "В этом месяце Вы потратили примерно столько же, сколько в предыдущем"


class MakingResultService(QThread):
    """Сценарий перехода от выбора категорий до финальной страницы"""
    send_total = Signal(int)
    progress = Signal()
    start_process = Signal()
    finish_process = Signal()
    send_comparison = Signal(Dynamic, str)
    send_now_month_summ = Signal(int)
    send_forecast = Signal(str)

    def __init__(
            self,
            table_model: TableModel,
            month_model: MonthModel,
            products_model: ProductsModel,
            categories_model: CategoriesModel,
    ):
        super().__init__()
        self.table_model = table_model
        self.month_model = month_model
        self.products_model = products_model
        self.categories_model = categories_model

    def run(self):
        self.send_total.emit(self.products_model.count() + 3)
        self.start_process.emit()

        new_data_writer = WriteNewData()
        new_data_writer.progress_updated.connect(self.progress.emit)
        new_data_writer.sync_start(
            self.table_model.get_path(),
            self.month_model.get_month_index(),
            # Массив вида (Объект продукта, Объект его категории)
            [(product, self.categories_model.get_by_id(product.category_id)) for product in
             self.products_model.get_all()]
        )


        previous_month_summ = read_old_data(
            self.table_model.get_path(),
            self.month_model.get_month_index(),
            self.categories_model.get_all()
        )

        self.progress.emit()

        now_month_summ = self.products_model.get_total_cost()
        dynamic, text = make_comparison(
            previous_month_summ,
            now_month_summ
        )
        self.send_now_month_summ.emit(now_month_summ)
        self.send_comparison.emit(dynamic, text)

        self.progress.emit()

        forecast_text = make_forecast(
            previous_month_summ,
            now_month_summ
        )
        self.send_forecast.emit(forecast_text)

        self.progress.emit()

        self.finish_process.emit()
