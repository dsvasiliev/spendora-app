from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class PageTitle(QWidget):
    """Заголовок страницы"""
    def __init__(self, title: str, subtitle: str | None = None, align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(align)
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("subtitle")
            subtitle_label.setAlignment(align)
            layout.addWidget(subtitle_label)

        self.setLayout(layout)