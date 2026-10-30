"""Interactive scientific canvas with non-exportable navigation aids."""

from PySide6.QtCore import QLineF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class PedigreeView(QGraphicsView):
    zoomChanged = Signal(int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Canvas do heredograma")
        self._middle_panning = False
        self.grid_enabled = True

    @property
    def zoom_percent(self) -> int:
        return round(self.transform().m11() * 100)

    def set_zoom(self, percent: int) -> None:
        target = max(20, min(500, percent)) / 100
        current = self.transform().m11()
        self.scale(target / current, target / current)
        self.zoomChanged.emit(self.zoom_percent)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)
        if not self.grid_enabled:
            return
        step = 40
        left = int(rect.left()) - (int(rect.left()) % step)
        top = int(rect.top()) - (int(rect.top()) % step)
        lines = [
            QLineF(x, rect.top(), x, rect.bottom())
            for x in range(left, int(rect.right()), step)
        ]
        lines += [
            QLineF(rect.left(), y, rect.right(), y)
            for y in range(top, int(rect.bottom()), step)
        ]
        painter.setPen(QPen(QColor("#E5EAF0"), 0))
        painter.drawLines(lines)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            next_scale = self.transform().m11() * factor
            if 0.2 <= next_scale <= 5.0:
                self.scale(factor, factor)
                self.zoomChanged.emit(self.zoom_percent)
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._middle_panning = True
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            synthetic = QMouseEvent(
                event.type(),
                event.position(),
                event.globalPosition(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                event.modifiers(),
            )
            super().mousePressEvent(synthetic)
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._middle_panning and event.button() == Qt.MouseButton.MiddleButton:
            synthetic = QMouseEvent(
                event.type(),
                event.position(),
                event.globalPosition(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
                event.modifiers(),
            )
            super().mouseReleaseEvent(synthetic)
            self._middle_panning = False
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            return
        super().mouseReleaseEvent(event)
