from PySide6.QtWidgets import QWidget, QVBoxLayout

from ui.patterns.page_title import PageTitle
from ui.patterns.plug import plug


class ProfilePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(PageTitle("Профиль"))
        layout.addWidget(plug(), 1)

        self.setLayout(layout)