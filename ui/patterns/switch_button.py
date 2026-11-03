from PySide6.QtCore import QPropertyAnimation, Property, Slot
from PySide6.QtGui import Qt, QPaintEvent, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget, QCheckBox


class SwitchButton(QCheckBox):
    """Кастомный переключатель"""
    def __init__(self, on: bool = False, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedWidth(44)
        self.setChecked(on)
        # self.setObjectName("switchButton")
        
        self._circle_position = 5

        # Анимация
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setDuration(200)
        # self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)

        self.stateChanged.connect(self.run_animation)

        self._active_pen = QPen(QColor("#BF6F4D"))
        self._active_pen.setWidth(2)
        self._not_active_pen = QPen(QColor("#898686"))
        self._not_active_pen.setWidth(2)
        self._active_brush = QBrush(QColor("#BF6F4D"))
        self._not_active_brush = QBrush(QColor("#898686"))
        # self.margin_animation.valueChanged.connect(self.on_margin_changed)
        
    @Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    @Slot(bool)
    def run_animation(self, value):
        self.animation.stop()

        if value:
            self.animation.setEndValue(25)
        else:
            self.animation.setEndValue(5)

        self.animation.start()

    def hitButton(self, pos, /):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        painter.setPen(self._active_pen if self.isChecked() else self._not_active_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(2, 2, 40, 20, 10, 10)

        painter.setBrush(self._active_brush if self.isChecked() else self._not_active_brush)
        painter.drawEllipse(self._circle_position, 5, 14, 14)
        painter.end()


