"""Interactive graphics view with bounded wheel zoom."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class PedigreeView(QGraphicsView):
    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            next_scale = self.transform().m11() * factor
            if 0.2 <= next_scale <= 5.0:
                self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)

