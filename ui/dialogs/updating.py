from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QWidget, QStackedWidget, QVBoxLayout, QLabel

from config import UPDATER_URL
# from app_context import MODEL
from infrastructure.network.download_update import DownloadUpdate
from ui.pages.main_steps.process_step import ProcessStep
from ui.patterns.buttons import PrimaryButton
from entities.dto.release import Release
from infrastructure.tools.styles import set_header_color, load_styles


class Updating(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle("Загрузка обновления...")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        main_layout = QVBoxLayout()
        self.central_widget = QStackedWidget()

        self.process_view = ProcessStep(None, "Скачивается обновление...", True)
        self.central_widget.addWidget(self.process_view)

        final_widget = QWidget()
        final_layout = QVBoxLayout()
        final_layout.setSpacing(25)
        final_layout.addStretch(1)
        title_label = QLabel("Обновление готово к установке")
        title_label.setObjectName("UpdatingTitleLabel")
        final_layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.news_label = QLabel()
        self.news_label.setWordWrap(True)
        final_layout.addWidget(self.news_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.run_button = PrimaryButton("Установить", True)
        # self.run_button.setAli
        self.run_button.clicked.connect(self.install_clicked)
        final_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignCenter)
        final_layout.addStretch(1)
        final_widget.setLayout(final_layout)

        self.file_path = ""

        self.central_widget.addWidget(final_widget)
        self.central_widget.setCurrentIndex(0)

        main_layout.addWidget(self.central_widget)
        self.setLayout(main_layout)

        # qss_path = MAIN_STYLES
        # if qss_path.exists():
        #     print("Стили установлены")
        #     self.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        # else:
        #     print("Файла не существует")

    def install_clicked(self):
        """Нажата кнопка 'Установить'. Запускаем установочник и закрываем приложение"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.file_path))
        exit(0)

    def download_finished(self, path: str) -> None:
        self.central_widget.setCurrentIndex(1)
        self.file_path = path

    def show_dialog(self, update_info: Release) -> int:
        """Показать меню"""
        news = ""
        for new in update_info.changes:
            news += f"- {new}\n"
        self.news_label.setText(news)

        thread = DownloadUpdate()
        thread.set_url(f'{UPDATER_URL}/{update_info.version}')
        thread.set_total.connect(self.process_view.set_max_value)
        thread.progress.connect(self.process_view.set_value)
        thread.finished.connect(self.download_finished)

        self.setMinimumSize(500, 400)
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        set_header_color(self)

        load_styles(self, "updating_dialog.qss")

        thread.start()

        return self.exec()


def show_updating_dialog(parent: QWidget, update_info: Release) -> None:
    """Запустить диалог в одну команду"""
    dialog = Updating(parent)
    dialog.show_dialog(update_info)
