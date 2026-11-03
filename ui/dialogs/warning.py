from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QDialog

# from main import app
from ui.patterns.buttons import PrimaryButton, MinimalButton
from infrastructure.tools.styles import set_header_color, load_styles


class WarningDialog(QDialog):
    ok = Signal()

    def __init__(self,
                 title: str,
                 text: str,
                 icon: QIcon,
                 parent: QWidget,
                 cancel_button: bool = True,
                 ok_text: str = "Ok"):
        super().__init__(parent)
        self.setWindowTitle(title)
        if not cancel_button:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        text_layout = QVBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(30, 30))
        text_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        text_layout.addWidget(QLabel(text))
        main_layout.addLayout(text_layout)

        buttons_layout = QHBoxLayout()
        if cancel_button:
            cancel_button_widget = MinimalButton("Отмена", active=True)
            cancel_button_widget.clicked.connect(self.close)
            buttons_layout.addWidget(cancel_button_widget, 0, Qt.AlignmentFlag.AlignLeft)
        ok_button = PrimaryButton(ok_text, active=True)
        ok_button.clicked.connect(self.ok_clicked)
        buttons_layout.addWidget(ok_button, 0, Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        load_styles(self, "warning_dialog.qss")

        self.adjustSize()  # подгоняем размер под содержимое
        size = self.size()
        self.setMinimumSize(size)
        self.setMaximumSize(size)

    def show_dialog(self):
        """Показать окно"""
        set_header_color(self)
        self.exec()

    def keyPressEvent(self, event: QKeyEvent):
        """Игнорирование нажатия Esc"""
        if event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)

    def ok_clicked(self):
        self.ok.emit()
        self.close()
