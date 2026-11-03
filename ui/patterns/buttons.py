from PySide6.QtGui import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel


class Button(QPushButton):
    """Кнопка"""

    def __init__(self,
                 text: str | None = None,
                 active: bool = False,
                 icon: QSvgWidget | None = None,
                 width: int = 150,
                 parent=None):
        super().__init__(parent)
        self.setEnabled(active)
        if icon:
            layout = QHBoxLayout(self)
            layout.setSpacing(10)
            icon.setFixedSize(20, 20)
            layout.addWidget(icon)
            if text:
                layout.addWidget(QLabel(text), 1, Qt.AlignmentFlag.AlignCenter)
        elif text:
            self.setText(text)
        self.setFixedWidth(width)


class MinimalButton(Button):
    """Обычная кнопка"""

    def __init__(self,
                 text: str | None = None,
                 active: bool = False,
                 icon: QSvgWidget | None = None,
                 width: int = 50,
                 parent=None):
        super().__init__(text, active, icon, width, parent)


class PrimaryButton(Button):
    """Кнопка с акцентом"""

    def __init__(self,
                 text: str | None = None,
                 active: bool = False,
                 icon: QSvgWidget | None = None,
                 width: int = 50,
                 parent=None):
        super().__init__(text, active, icon, width, parent)
