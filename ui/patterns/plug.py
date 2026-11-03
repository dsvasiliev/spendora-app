from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


def plug(text: str = "Блок в разработке") -> QLabel:
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label
