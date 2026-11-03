from pathlib import Path

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QFileDialog, \
    QStackedWidget, QScrollArea, QSizePolicy

from config import APP_NAME, MONTHS_RU, TABLES_URL
from infrastructure.tools.files import get_svg_widget, get_icon
from models.month_model import MonthModel
from models.receipts_model import ReceiptsModel
from models.table_model import TableModel
from services.read_receipts_service import ReadReceiptsService
from services.return_servise import ReturnService
from ui.patterns.buttons import MinimalButton, PrimaryButton
from ui.patterns.link_card import LinkCard
from ui.patterns.page_title import PageTitle
from ui.patterns.content_block import ContentBlock
from infrastructure.tools.open_url import open_url


def make_step_header(number: int, title: str, right_widget: QWidget | None = None) -> QHBoxLayout:
    """Верхняя часть блоков главной страницы"""
    header = QHBoxLayout()
    header.setSpacing(0)

    step_number_wrap = QWidget()
    step_number_wrap.setObjectName("stepNumberWrap")
    step_number_wrap.setFixedSize(36, 36)
    wrap_layout = QHBoxLayout()
    wrap_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
    step_number = QLabel(str(number))
    step_number.setObjectName("stepNumber")
    step_number.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
    wrap_layout.addWidget(step_number)
    step_number_wrap.setLayout(wrap_layout)

    title_label = QLabel(title)
    title_label.setObjectName("stepTitle")

    header.addWidget(step_number_wrap)
    header.addWidget(title_label)
    header.addStretch(1)

    if right_widget is not None:
        header.addWidget(right_widget)

    return header


class EmlFileRow(QWidget):
    """Строка списка выбранного .eml файла."""

    def __init__(self, path: str, on_remove, parent=None):
        super().__init__(parent)
        self._path = path
        self.setObjectName("emlFileRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        icon = QLabel()
        icon.setObjectName("emlFileRowIcon")
        icon.setPixmap(get_icon("File-icon.svg").pixmap(22, 22))
        icon.setFixedSize(22, 22)

        name_label = QLabel(Path(path).name)
        name_label.setObjectName("emlFileRowLabel")

        remove_btn = QPushButton()
        remove_btn.setObjectName("emlFileRemoveBtn")
        remove_btn.setIcon(get_icon("Trash.svg"))
        remove_btn.setIconSize(QSize(18, 18))
        remove_btn.setFixedSize(18, 18)
        remove_btn.clicked.connect(lambda: on_remove(self._path))

        layout.addWidget(icon)
        layout.addWidget(name_label, 1)
        layout.addWidget(remove_btn)

    @property
    def path(self):
        return self._path


class UploadCheckCard(ContentBlock):
    """Блок загрузки чеков с выбором .eml и списком файлов."""
    ready = Signal(bool)

    def __init__(
            self,
            receipts_model: ReceiptsModel,
            parent=None
    ):
        super().__init__(accent=True, parent=parent)
        self.receipts_model = receipts_model
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)

        self._open_btn = MinimalButton("Открыть", active=True)
        self._open_btn.clicked.connect(self._pick_files)
        main_layout.addLayout(make_step_header(1, "Чеки", self._open_btn))

        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        empty_page = QWidget()
        empty_layout = QVBoxLayout(empty_page)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel()
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon.setPixmap(get_icon("Big_file_icon.svg").pixmap(100, 100))

        hint_main = QLabel(
            "Перетащите .eml или .html файлы или выберите с устройства\n"
            "Можно загрузить сразу несколько писем"
        )
        hint_main.setObjectName("hintFile")
        hint_main.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(hint_main)

        list_page = QWidget()
        list_layout = QVBoxLayout(list_page)
        list_layout.setContentsMargins(0, 20, 0, 0)
        list_layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._rows_host = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_host)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(4)
        self._rows_layout.addStretch(1)

        self._scroll.setWidget(self._rows_host)
        list_layout.addWidget(self._scroll, 1)

        clear_wrap = QHBoxLayout()
        clear_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._clear_btn = MinimalButton("", icon=get_svg_widget("X.svg"), active=True)
        self._clear_btn.setObjectName("emlClearAllBtn")
        self._clear_btn.clicked.connect(self.reset)
        clear_wrap.addWidget(self._clear_btn)
        list_layout.addLayout(clear_wrap)

        self._stack.addWidget(empty_page)
        self._stack.addWidget(list_page)
        main_layout.addWidget(self._stack, 1)


    def _pick_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите письма",
            "",
            "Чеки (*.eml *.html)",
        )
        if paths:
            self._add_paths(paths)

    def _add_paths(self, paths: list[str]) -> None:
        """Добавление новых файлов"""
        added_paths = self.receipts_model.add_paths(paths)
        for index, path in added_paths:
            self._rows_layout.insertWidget(
                index - 1,
                EmlFileRow(path, self._remove_path)
            )
        if len(added_paths) > 0:
            self.ready.emit(True)
            self._stack.setCurrentIndex(1)

    def _remove_path(self, path: str) -> None:
        if self.receipts_model.remove_path(path):
            for index in range(self._rows_layout.count()):
                item = self._rows_layout.itemAt(index)
                widget = item.widget() if item else None
                if isinstance(widget, EmlFileRow) and widget.path == path:
                    widget.deleteLater()
                    break
        if self.receipts_model.is_empty():
            self._show_empty()

    def reset(self) -> None:
        """Удаление всех фалов"""
        self.receipts_model.reset()
        for index in reversed(range(self._rows_layout.count())):
            item = self._rows_layout.itemAt(index)
            widget = item.widget() if item else None
            if isinstance(widget, EmlFileRow):
                widget.deleteLater()
        self._show_empty()

    def _show_empty(self) -> None:
        self.ready.emit(False)
        self._stack.setCurrentIndex(0)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls() and any(
                url.toLocalFile().lower().endswith(".eml") or url.toLocalFile().lower().endswith(".html")
                for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.toLocalFile().lower().endswith(".eml") or url.toLocalFile().lower().endswith(".html")
        ]
        if paths:
            self._add_paths(paths)
            event.acceptProposedAction()
        else:
            event.ignore()


class UploadTableCard(ContentBlock):
    """Блок загрузки одной таблицы .xlsx."""
    ready = Signal(bool)

    def __init__(
            self,
            table_model: TableModel,
            parent: QWidget | None = None
    ):
        super().__init__(parent=parent)
        self.table_model = table_model
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)

        self._open_btn = MinimalButton("Открыть", active=True)
        self._open_btn.clicked.connect(self._pick_file)
        main_layout.addLayout(make_step_header(3, "Таблица", self._open_btn))

        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        empty_page = QWidget()
        empty_layout = QHBoxLayout(empty_page)
        empty_layout.setSpacing(0)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel()
        empty_icon.setPixmap(get_icon("Big_table_icon.svg").pixmap(90, 90))

        hint_file = QLabel("Загрузите .xlsx шаблон или\nиспользуйте готовый")
        hint_file.setObjectName("hintTable")
        hint_file.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(hint_file)

        selected_page = QWidget()
        selected_layout = QVBoxLayout(selected_page)
        selected_layout.setContentsMargins(0, 20, 0, 0)
        selected_layout.setSpacing(16)

        panel_wrap = QHBoxLayout()
        panel_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._file_panel = QFrame()
        self._file_panel.setObjectName("tableFilePanel")
        panel_layout = QHBoxLayout(self._file_panel)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.setContentsMargins(30, 15, 30, 15)
        panel_layout.setSpacing(16)

        self._file_icon = QLabel()
        self._file_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            self._file_icon.setPixmap(get_icon("Selected_table.svg").pixmap(24, 24))
        except FileNotFoundError:
            pass

        self._file_name_label = QLabel()
        self._file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self._file_name.setWordWrap(True)

        panel_layout.addWidget(self._file_icon)
        panel_layout.addWidget(self._file_name_label)
        panel_wrap.addWidget(self._file_panel)
        selected_layout.addLayout(panel_wrap, 1)

        clear_wrap = QHBoxLayout()
        clear_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._clear_btn = MinimalButton("", icon=get_svg_widget("X.svg"), active=True)
        self._clear_btn.setObjectName("tableClearBtn")
        self._clear_btn.clicked.connect(self._clear)
        clear_wrap.addWidget(self._clear_btn)
        selected_layout.addLayout(clear_wrap)

        self._stack.addWidget(empty_page)
        self._stack.addWidget(selected_page)
        main_layout.addWidget(self._stack, 1)

    def _pick_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите таблицу",
            "",
            "Таблицы (*.xlsx)",
        )
        if path:
            self._set_path(path)

    def _set_path(self, path: str) -> None:
        if not path.lower().endswith(".xlsx"):
            return
        self.table_model.set_path(path)
        self._file_name_label.setText(self.table_model.get_name())
        self._show_selected()

    def _clear(self) -> None:
        self.table_model.reset()
        self._file_name_label.clear()
        self._show_empty()

    def _show_selected(self) -> None:
        self.ready.emit(True)
        self._stack.setCurrentIndex(1)

    def _show_empty(self) -> None:
        self.ready.emit(False)
        self._stack.setCurrentIndex(0)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls() and any(
                url.toLocalFile().lower().endswith(".xlsx") for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            local_path = url.toLocalFile()
            if local_path.lower().endswith(".xlsx"):
                self._set_path(local_path)
                event.acceptProposedAction()
                return
        event.ignore()


class StartStep(QWidget):
    def __init__(
            self,
            receipts_model: ReceiptsModel,
            table_model: TableModel,
            month_model: MonthModel,
            read_receipts_service: ReadReceiptsService,
            return_service: ReturnService,
    ):
        super().__init__()

        # Параметры подсветки элементов
        self.elems_to_highlight: list[ContentBlock] = []
        self.active_list: list[bool] = []
        self.active_elem: ContentBlock

        main_area = QVBoxLayout()

        heading_layout = QHBoxLayout()
        heading_layout.setSpacing(15)

        heading_layout.addWidget(
            PageTitle(APP_NAME, "Загрузите чеки — мы разберём покупки и покажем, куда уходят деньги"),
            1
        )

        # TODO: включить при умном анализе расходов
        # analysis_label = QLabel("Анализ расходов")
        # switch = SwitchButton()
        #
        # heading_layout.addWidget(analysis_label)
        # heading_layout.addWidget(switch)
        self._start_button = PrimaryButton("Начать")
        self._start_button.clicked.connect(read_receipts_service.start)
        heading_layout.addWidget(self._start_button)

        central_layout = QHBoxLayout()
        content_widget = QWidget()
        content_widget.setMaximumSize(QSize(1400, 700))
        central_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(content_widget)
        content = QHBoxLayout(content_widget)
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(12)

        # TODO: автоматическая загрузка чеков
        # left.addWidget(LinkCard("Чеки можно загрузить быстрее: просто подключите Вашу почту"))

        upload_check_card = UploadCheckCard(receipts_model)
        self.upload_check_card = upload_check_card
        self.elems_to_highlight.append(upload_check_card)
        self.active_list.append(False)
        self.active_elem = upload_check_card
        upload_check_card.ready.connect(lambda active: self.set_active(0, active))
        left.addWidget(upload_check_card, 1)

        right = QVBoxLayout()
        right.setSpacing(12)

        month_card = ContentBlock()

        month_card_header = make_step_header(2, "Выберите месяц")

        month_combo = QComboBox()
        month_combo.addItems(MONTHS_RU)
        month_combo.setObjectName("monthCombo")
        month_combo.currentIndexChanged.connect(lambda index: month_model.set_month_index(index))
        current_month_index = month_model.get_month_index()
        month_combo.setCurrentIndex(current_month_index)

        month_card_header.addWidget(month_combo)
        month_card.setLayout(month_card_header)

        right.addWidget(month_card)

        download_template_card = LinkCard("Шаблоны под разные задачи можно загрузить в нашем сайте")
        download_template_card.clicked.connect(lambda: open_url(TABLES_URL))
        right.addWidget(download_template_card)

        upload_table_card = UploadTableCard(table_model)
        self.upload_table_card = upload_table_card
        self.elems_to_highlight.append(upload_table_card)
        self.active_list.append(False)
        upload_table_card.ready.connect(lambda active: self.set_active(1, active))
        right.addWidget(upload_table_card, 1)

        content.addLayout(left, 1)
        content.addLayout(right, 1)
        main_area.addLayout(heading_layout)
        main_area.addLayout(central_layout, 1)

        self.setLayout(main_area)

        return_service.start_process.connect(self.upload_check_card.reset)

    def set_active(self, index: int, active: bool):
        self.active_list[index] = active
        self.active_elem.not_accent()
        if all(self.active_list):
            self._start_button.setEnabled(True)
        else:
            self._start_button.setEnabled(False)
            for i in range(len(self.elems_to_highlight)):
                if not self.active_list[i]:
                    self.elems_to_highlight[i].accent()
                    self.active_elem = self.elems_to_highlight[i]
                    break
