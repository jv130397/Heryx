"""Interactive scientific canvas with non-exportable navigation aids."""

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class PedigreeView(QGraphicsView):
    zoomChanged = Signal(int)
    viewportChanged = Signal()

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
        self.floating_control = None
        self.minimum_zoom = 5
        self.maximum_zoom = 500
        self.horizontalScrollBar().valueChanged.connect(self.viewportChanged)
        self.verticalScrollBar().valueChanged.connect(self.viewportChanged)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.floating_control is not None:
            control = self.floating_control
            control.adjustSize()
            control.move(
                self.viewport().width() - control.width() - 18,
                self.viewport().height() - control.height() - 18,
            )
        self.viewportChanged.emit()

    @property
    def zoom_percent(self) -> int:
        return round(self.transform().m11() * 100)

    def set_zoom(self, percent: int, focal_point: QPointF | None = None) -> None:
        """Set zoom while preserving either the requested focal point or view center."""
        target = max(self.minimum_zoom, min(self.maximum_zoom, percent)) / 100
        focal = focal_point or self.mapToScene(self.viewport().rect().center())
        current = self.transform().m11()
        self.scale(target / current, target / current)
        self.centerOn(focal)
        self.zoomChanged.emit(self.zoom_percent)
        self.viewportChanged.emit()

    def reset_zoom(self) -> None:
        self.set_zoom(100)

    def center_smoothly(self, point: QPointF) -> None:
        """Navigation hook kept deterministic when reduced motion is active."""
        self.centerOn(point)
        self.viewportChanged.emit()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)
        if not self.grid_enabled:
            return
        scale = self.transform().m11()
        # At overview zoom a dense grid competes with relationship lines.
        if scale < 0.3:
            return
        step = 80 if scale < 0.65 else 40
        left = int(rect.left()) - (int(rect.left()) % step)
        top = int(rect.top()) - (int(rect.top()) % step)
        lines = [
            QLineF(x, rect.top(), x, rect.bottom()) for x in range(left, int(rect.right()), step)
        ]
        lines += [
            QLineF(rect.left(), y, rect.right(), y) for y in range(top, int(rect.bottom()), step)
        ]
        grid = QColor("#DDE2E6")
        grid.setAlpha(150 if scale >= 0.65 else 105)
        painter.setPen(QPen(grid, 0))
        painter.drawLines(lines)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            next_scale = self.transform().m11() * factor
            if self.minimum_zoom / 100 <= next_scale <= self.maximum_zoom / 100:
                self.scale(factor, factor)
                self.zoomChanged.emit(self.zoom_percent)
                self.viewportChanged.emit()
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
            self.viewportChanged.emit()
            return
        super().mouseReleaseEvent(event)
