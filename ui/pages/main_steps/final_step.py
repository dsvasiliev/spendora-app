from pathlib import Path

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from config import SURVEY_URL
from entities.dto.dynamic import Dynamic
from infrastructure.tools.open_url import open_url
from infrastructure.tools.text import format_number
from infrastructure.tools.files import get_svg_widget, get_icon
from models.products_model import ProductsModel
from models.table_model import TableModel
from services.making_result_service import MakingResultService
from services.return_servise import ReturnService
# from app_context import MODEL
from ui.patterns.buttons import PrimaryButton
from ui.patterns.content_block import ContentBlock
from ui.patterns.link_card import LinkCard
from ui.patterns.page_title import PageTitle


def build_title(title: str) -> QLabel:
    """Создание заголовка для блока"""
    title = QLabel(title)
    title.setObjectName("finalCardTitle")
    return title


class TotalCard(ContentBlock):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(False, parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(10)

        layout.addWidget(build_title("Итого"))

        amount_row = QHBoxLayout()
        amount_row.setSpacing(20)

        self.amount = QLabel()
        self.amount.setObjectName("finalTotalAmount")

        self.trend_widget = QWidget()
        trend_layout = QHBoxLayout(self.trend_widget)
        trend_layout.setSpacing(20)

        self.trend_icon = QLabel()
        self.trend_icon.setObjectName("finalTrendIcon")

        self.trend_text = QLabel()
        self.trend_text.setWordWrap(True)

        trend_layout.addWidget(self.trend_icon, 0)
        trend_layout.addWidget(self.trend_text, 0)

        amount_row.addWidget(self.amount, 1)
        amount_row.addWidget(self.trend_widget, 1)
        layout.addLayout(amount_row, 1)

    def set_comparison(
            self,
            dynamic: Dynamic,
            text: str,
    ) -> None:
        """Выводим данные о сравнении с предыдущим месяцем"""
        if text == '':
            self.trend_widget.setVisible(False)
        else:
            self.trend_widget.setVisible(True)
            if dynamic == Dynamic.NEGATIVE:
                self.trend_icon.setPixmap(get_icon("Trending_up.svg").pixmap(20, 20))
            elif dynamic == Dynamic.POSITIVE:
                self.trend_icon.setPixmap(get_icon("Trending_down.svg").pixmap(20, 20))
            else:
                self.trend_icon.setPixmap(get_icon("No_trending.svg").pixmap(20, 20))
            self.trend_text.setText(text)

    def set_total_amount(self, total_amount: float):
        """выводим данные о суммарных расходах"""
        self.amount.setText(f"{format_number(round(total_amount, 2))} ₽")


class ForecastCard(ContentBlock):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(False, parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(10)

        layout.addWidget(build_title("Прогноз на следующий месяц"))

        self.text = QLabel()
        self.text.setWordWrap(True)
        self.text.setTextFormat(Qt.TextFormat.RichText)

        layout.addWidget(self.text, 1)

    def set_forecast(self, text: str) -> None:
        self.text.setText(text)
        #     self.text.setText(
        #         f'Если траты не изменятся, вы потратите <span style="font-weight:600;">{format_number(forecast)} ₽</span>')
        # else:
        #     self.text.setText("К сожалению, недостаточно данных для формирования прогноза")


def open_table(path: Path):
    """Показать пользователю таблицу"""
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


class FinalView(QWidget):
    def __init__(
            self,
            table_model: TableModel,
            products_model: ProductsModel,
            making_result_service: MakingResultService,
            return_service: ReturnService,
            parent: QWidget | None = None
    ):
        super().__init__(parent)

        self.table_model = table_model
        self.products_model = products_model

        layout = QVBoxLayout(self)
        layout.setSpacing(24)

        layout.addWidget(
            PageTitle(
                "Отчёт готов",
                "Мы проанализировали ваши расходы за месяц",
                Qt.AlignmentFlag.AlignCenter,
            )
        )

        all_cards = QHBoxLayout()
        all_cards.setSpacing(16)

        self.total_card = TotalCard()
        self.forecast_card = ForecastCard()
        open_next = LinkCard(
            "Посмотреть другие месяцы или загрузить новые чеки",
            True,
            "Double_arrow.svg"
        )
        open_next.clicked.connect(return_service.sync_start)

        survey_link = LinkCard(
            "Поделитесь Вашим мнением о приложении",
        )
        survey_link.clicked.connect(lambda: open_url(SURVEY_URL))

        left_layout = QVBoxLayout()
        left_layout.setSpacing(16)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)

        left_layout.addWidget(self.total_card, 0)

        right_layout.addWidget(self.forecast_card, 0)
        right_layout.addWidget(open_next, 0)

        all_cards.addLayout(left_layout, 1)
        all_cards.addLayout(right_layout, 1)
        layout.addLayout(all_cards, 0)
        layout.addWidget(survey_link)
        layout.addStretch()

        open_table_btn = PrimaryButton(
            "Открыть таблицу",
            True,
            get_svg_widget("White_table.svg"),
        )
        open_table_btn.setObjectName("open_table_button")
        open_table_btn.clicked.connect(lambda: open_table(self.table_model.get_path()))
        layout.addWidget(open_table_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        making_result_service.send_now_month_summ.connect(self.total_card.set_total_amount)
        making_result_service.send_comparison.connect(self.total_card.set_comparison)
        making_result_service.send_forecast.connect(self.forecast_card.set_forecast)
