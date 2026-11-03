from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from infrastructure.tools.files import get_svg_widget
from ui.patterns.content_block import ContentBlock


class LinkCard(ContentBlock):
    clicked = Signal()

    """Блок ссылки-подсказки"""
    def __init__(self, text: str, accent: bool = False, svg_link: str = "Arrow.svg", parent: QWidget | None =None):
        super().__init__(accent, parent)

        layout = QHBoxLayout(self)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setObjectName("cardText")
        layout.addWidget(label, 1)

        arrow_widget = get_svg_widget(svg_link)
        arrow_widget.setObjectName("linkArrow")
        layout.addWidget(arrow_widget)

    def mouseReleaseEvent(self, event, /):
        self.clicked.emit()