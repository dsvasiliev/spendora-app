from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import QHBoxLayout, QWidget, QMainWindow, QStackedWidget

from config import APP_NAME, VERSION, ACTUAL_INFO_URL, IMPORTANT_INFO_URL
from ui.dialogs.updating import show_updating_dialog
from ui.dialogs.warning import WarningDialog
from app_context import AppContext
from infrastructure.network.load_update_info import LoadUpdateInfo
from entities.dto.release import Release
from infrastructure.tools.styles import set_header_color, load_styles
from infrastructure.tools.files import get_icon
from ui.pages.main import MainPage
from ui.pages.recent import RecentPage
from ui.pages.settings import SettingsPage
from ui.pages.profile import ProfilePage
from ui.sidebar import Sidebar
from infrastructure.tools.is_new_version import is_new_version


class MainWindow(QMainWindow):
    def __init__(
            self,
            app_context: AppContext,
    ) -> None:
        super().__init__()
        # Настройка окна
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(get_icon("MAIN.ico"))
        self.setMinimumSize(1000, 600)
        set_header_color(self)

        main_widget = QWidget()
        root = QHBoxLayout(main_widget)

        self.content_widget = QStackedWidget()
        self.content_widget.setObjectName("ContentWidget")

        main_page = MainPage(app_context)
        recent_page = RecentPage()
        profile_page = ProfilePage()
        settings_page = SettingsPage()

        self.content_widget.addWidget(main_page)
        self.content_widget.addWidget(recent_page)
        self.content_widget.addWidget(settings_page)
        self.content_widget.addWidget(profile_page)

        self.content_widget.setCurrentIndex(0)

        sidebar = Sidebar()
        sidebar.page_changed.connect(self.change_page)

        root.addWidget(sidebar)
        root.addWidget(self.content_widget)
        self.setCentralWidget(main_widget)
        load_styles(self,"main_window.qss")

        # Проверить наличие обновлений через 2 сек.
        self.update_checker = LoadUpdateInfo(ACTUAL_INFO_URL, IMPORTANT_INFO_URL, self)
        self.update_checker.finished.connect(self.has_updates)
        QTimer.singleShot(2000, self.update_checker.start)

        # Очистить старые данные из бд через 1 сек.
        QTimer.singleShot(1000, app_context.db_clean_service.start)

    def has_updates(self, actual_version: Release, important_version: Release) -> None:
        """При необходимости показать меню обновления"""
        if is_new_version(actual_version.version, VERSION):
            notification = WarningDialog(
                "Доступно обновление",
                "Доступна новая версия приложения",
                get_icon("update.svg"),
                self,
                ok_text="Скачать",
                cancel_button=not is_new_version(important_version.version, VERSION),
            )
            notification.ok.connect(lambda: show_updating_dialog(self, actual_version))
            notification.show_dialog()

    # def _menu_test(self):
    #     trigger = QPushButton("Выбрать категорию", self)
    #     trigger.setGeometry(40, 40, 200, 40)
    #     trigger.clicked.connect(self._show_dialog)
    #
    # def _show_dialog(self):
    #     DIALOGS.category_select_dialog.reset()
    #     DIALOGS.category_select_dialog.set_comparison()
    #     print(DIALOGS.category_select_dialog.show_dialog(3))

    @Slot()
    def change_page(self, index: int) -> None:
        self.content_widget.setCurrentIndex(index)