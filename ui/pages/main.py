from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QStackedWidget, QWidget

from ui.dialogs.select_category import CategorySelectDialog
from app_context import AppContext
from ui.dialogs.warning import WarningDialog
from ui.pages.main_steps.final_step import FinalView
from ui.pages.main_steps.process_step import ProcessStep
from ui.pages.main_steps.select_category_step import SelectCategoryStep
from ui.pages.main_steps.start_step import StartStep
from infrastructure.tools.files import get_path, get_icon


class MainPage(QStackedWidget):
    def __init__(
            self,
            app_context: AppContext,
    ):
        super().__init__()

        # Диалог выбора категорий
        self.category_select_dialog = CategorySelectDialog(
            app_context.categories_model,
            app_context.groups_model,
            self
        )
        qss_path = get_path("src", "styles", "select_category_menu.qss")
        if qss_path.exists() and self.category_select_dialog:
            self.category_select_dialog.setStyleSheet(qss_path.read_text(encoding="utf-8"))

        # Начальная страница
        self._start_view = StartStep(
            app_context.receipts_model,
            app_context.table_model,
            app_context.month_model,
            app_context.read_receipts_service,
            app_context.return_service
        )
        self.addWidget(self._start_view)

        # Выбор категорий для каждого продукта
        self._select_category_view = SelectCategoryStep(
            app_context.categories_model,
            app_context.products_model,
            self.category_select_dialog,
            app_context.making_result_service,
            app_context.select_categories_service
        )
        self.addWidget(self._select_category_view)

        # Финальная страница с результатами
        self._final_view = FinalView(
            app_context.table_model,
            app_context.products_model,
            app_context.making_result_service,
            app_context.return_service
        )
        self.addWidget(self._final_view)

        # Ожидание 1: обработка чеков
        self._first_waiting = ProcessStep(text="Обработка чеков...")
        self.addWidget(self._first_waiting)

        app_context.read_receipts_service.send_total.connect(self._first_waiting.set_max_value)
        app_context.read_receipts_service.progress.connect(self._first_waiting.add_value)
        app_context.read_receipts_service.start_process.connect(lambda: self.setCurrentWidget(self._first_waiting))
        app_context.read_receipts_service.finished.connect(self.category_select_dialog.update_data)
        app_context.read_receipts_service.finished.connect(self._select_category_view.update_data)
        app_context.read_receipts_service.finished.connect(lambda: self.start_timer_to(self._select_category_view))
        app_context.read_receipts_service.error.connect(self.show_parsing_error)

        # Ожидание 2: запись в таблицу и подготовка отсчёта
        self._second_waiting = ProcessStep(get_icon("Big_AI.svg"), "Записываем расходы и готовим выводы…")
        self.addWidget(self._second_waiting)

        app_context.making_result_service.send_total.connect(self._second_waiting.set_max_value)
        app_context.making_result_service.progress.connect(self._second_waiting.add_value)
        app_context.making_result_service.start_process.connect(lambda: self.setCurrentWidget(self._second_waiting))
        app_context.making_result_service.finish_process.connect(lambda: self.start_timer_to(self._final_view))

        # Переход к новому месяцу
        app_context.return_service.process_finished.connect(lambda: self.setCurrentWidget(self._start_view))


        # MODEL.file_is_writing.connect(self._second_waiting.add_value)
        # MODEL.file_writing_end.connect(self.to_final_view)



        self.setCurrentIndex(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_is_out)
        self._target_page: QWidget | None = None

        self.statistic_worker = None

    # def to_first_waiting(self):
    #     """Переход к первому ожиданию"""
    #     self._first_waiting.set_max_value(count(MODEL.file_names) + 2)
    #     self._first_waiting.set_value(0)
    #     self._first_waiting.set_text(f"Загружено чеков: {count(MODEL.file_names)}\n Обработка...")
    #     self.setCurrentWidget(self._first_waiting)
    #     MODEL.parse()

    # def to_select_category_view(self):
    #     """Переход к выбору категорий"""
    #     # Обновляем диалоговое окно выбора категории
    #     self.category_select_dialog.reset()
    #     self.category_select_dialog.set_comparison()
    #     self._select_category_view.set_comparison()
    #     self.start_timer_to(self._select_category_view)

    # def to_second_waiting(self):
    #     """Переход ко второму ожиданию"""
    #     self._second_waiting.set_max_value(count(MODEL.get_all()) + 1)
        # self._second_waiting.set_value(0)
        # self.setCurrentWidget(self._second_waiting)
        # MODEL.write_func()

    # def to_final_view(self):
    #     """Переход к финальной странице с результатами"""
    #     self._final_view.set_comparison()
    #     self.start_timer_to(self._final_view)

    # def to_start_view(self):
    #     """Переход к начальной странице для повторного использования"""
        # self.statistic_worker = SendStatistic('continue')
        # self.statistic_worker.start()
        # self._start_view.reset()
        # self.setCurrentWidget(self._start_view)

    def show_parsing_error(self, path: str):
        print('ошибка')
        notification = WarningDialog(
                "Ошибка",
                f'Не удалось обработать чек: {path}',
                get_icon("Warning.svg"),
                self,
                ok_text="Ок",
            )
        notification.show_dialog()


    def start_timer_to(self, target_page: QWidget, milliseconds: int = 500):
        """Перейти на другую страницу через несколько миллисекунд"""
        self.timer.setInterval(milliseconds)
        self.timer.start()
        self._target_page = target_page

    def _timer_is_out(self):
        """Перемещаемся на следующую страницу"""
        self.timer.stop()
        if self._target_page:
            self.setCurrentWidget(self._target_page)
