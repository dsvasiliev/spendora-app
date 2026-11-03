from PySide6.QtCore import QSize, Slot, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton

from infrastructure.tools.files import get_icon


class Sidebar(QFrame):
    """Сайдбар всего приложения"""
    page_changed = Signal(int)

    def __init__(self, current_index: int = 0, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")

        self.current_index = current_index

        self.buttons: list[QPushButton] = []
        sidebar_layout = QVBoxLayout(self)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        nav_main = QPushButton()
        nav_main.setObjectName("navButton")
        nav_main.setIcon(get_icon("sidebar", "Main_page.svg"))
        nav_main.clicked.connect(lambda: self.on_click(0))
        self.buttons.append(nav_main)

        nav_recent = QPushButton()
        nav_recent.setObjectName("navButton")
        nav_recent.setIcon(get_icon("sidebar", "Recent.svg"))
        nav_recent.clicked.connect(lambda: self.on_click(1))
        self.buttons.append(nav_recent)

        nav_settings = QPushButton()
        nav_settings.setObjectName("navButton")
        nav_settings.setIcon(get_icon("sidebar", "Settings.svg"))
        nav_settings.clicked.connect(lambda: self.on_click(2))
        self.buttons.append(nav_settings)

        nav_profile = QPushButton()
        nav_profile.setObjectName("navButton")
        nav_profile.setIcon(get_icon("sidebar", "Profile.svg"))
        nav_profile.clicked.connect(lambda: self.on_click(3))
        self.buttons.append(nav_profile)

        self.make_active(current_index)

        for nav_button in (nav_main, nav_recent, nav_profile, nav_settings):
            nav_button.setIconSize(QSize(18, 18))

        sidebar_layout.addWidget(nav_main)
        sidebar_layout.addWidget(nav_recent)
        sidebar_layout.addWidget(nav_settings)
        sidebar_layout.addStretch(1)
        sidebar_layout.addWidget(nav_profile)

    def make_not_active(self, number: int):
        button = self.buttons[number]
        button.setStyleSheet("")  # Очищаем
        # button.styles().unpolish(button)  # Сбрасываем

    def make_active(self, number: int):
        self.buttons[number].setStyleSheet("background-color: #fff;")  # Устанавливаем новый

    @Slot()
    def on_click(self, number: int):
        if self.current_index == number:
            return
        self.make_not_active(self.current_index)
        self.current_index = number
        self.make_active(self.current_index)
        self.page_changed.emit(number)
