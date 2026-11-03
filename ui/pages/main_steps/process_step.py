from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar


class ProcessStep(QWidget):
    """Страница ожидания"""

    def __init__(self,
                 icon: QIcon | None = None,
                 text: str | None = None,
                 progress_bar: bool = True
                 ):
        super().__init__()
        self._progress_value = 0
        self._progress_max_value = 0

        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.setSpacing(30)

        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(70, 70))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(icon_label)

        self.text_label = QLabel()

        if text:
            self.text_label.setText(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.text_label)

        self.progress_bar: QProgressBar | None = None
        if progress_bar:
            self.progress_bar = QProgressBar()
            if self.progress_bar:
                self.progress_bar.setTextVisible(False)
                main_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def set_max_value(self, value: int):
        if self.progress_bar:
            self._progress_max_value = value
            self.progress_bar.setMaximum(value)
            self.set_value(0)

    def set_value(self, value: int):
        if self.progress_bar:
            self._progress_value = value
            self.progress_bar.setValue(value)

    def add_value(self):
        self._progress_value += 1
        self.set_value(self._progress_value)

    def set_text(self, text: str):
        """Задать новый текст"""
        self.text_label.setText(text)
