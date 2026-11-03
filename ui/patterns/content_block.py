from PySide6.QtWidgets import QFrame


class ContentBlock(QFrame):
    def __init__(self, accent: bool = False, parent=None):
        super().__init__(parent)
        if accent:
            self.accent()
        else:
            self.not_accent()

    def accent(self):
        self.setStyleSheet("ContentBlock {border: 2px solid #d4b0a0;}")

    def not_accent(self):
        self.setStyleSheet("ContentBlock {border: 2px solid #fff;}")
