"""Qt graphics items implementing the confirmed basic pedigree symbols."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsObject,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from rarepedigree.domain import (
    GenderIdentity,
    Individual,
    ObservationStatus,
    Relationship,
    RelationshipKind,
)

SYMBOL_SIZE = 48.0


class IndividualItem(QGraphicsObject):
    """Movable symbol whose geometry is derived from, but does not mutate, clinical data."""

    def __init__(
        self,
        person: Individual,
        on_moved: Callable[[IndividualItem, QPointF, QPointF], None] | None = None,
    ) -> None:
        super().__init__()
        self.person = person
        self._on_moved = on_moved
        self._drag_start = QPointF()
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setPos(person.layout.x, person.layout.y)
        self.setToolTip(person.label)

    def boundingRect(self) -> QRectF:
        return QRectF(-35, -35, 70, 88)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        half = SYMBOL_SIZE / 2
        if self.person.gender_identity == GenderIdentity.MAN:
            path.addRect(QRectF(-half, -half, SYMBOL_SIZE, SYMBOL_SIZE))
        elif self.person.gender_identity == GenderIdentity.WOMAN:
            path.addEllipse(QRectF(-half, -half, SYMBOL_SIZE, SYMBOL_SIZE))
        else:
            polygon = QPolygonF(
                [QPointF(0, -half), QPointF(half, 0), QPointF(0, half), QPointF(-half, 0)]
            )
            path.addPolygon(polygon)
        return path

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        del option, widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        selected = self.isSelected()
        pen = QPen(QColor("#1769aa") if selected else QColor("#20262e"), 2.5 if selected else 2)
        painter.setPen(pen)
        status = self.person.phenotype_status
        brush_color = (
            QColor("#20262e") if status == ObservationStatus.PRESENT else QColor("#ffffff")
        )
        painter.setBrush(QBrush(brush_color))
        painter.drawPath(self.shape())

        if status == ObservationStatus.UNKNOWN:
            painter.setPen(QPen(QColor("#5b6573"), 2))
            font = painter.font()
            font.setBold(True)
            font.setPointSize(15)
            painter.setFont(font)
            painter.drawText(QRectF(-12, -15, 24, 30), Qt.AlignmentFlag.AlignCenter, "?")

        painter.setPen(QPen(QColor("#20262e"), 2))
        half = SYMBOL_SIZE / 2
        if self.person.deceased:
            painter.drawLine(QPointF(-half - 5, half + 5), QPointF(half + 5, -half - 5))
        if self.person.proband or self.person.consultand:
            painter.drawLine(QPointF(-half - 22, half + 14), QPointF(-half - 3, half - 3))
            painter.drawLine(QPointF(-half - 3, half - 3), QPointF(-half - 10, half - 1))
            painter.drawLine(QPointF(-half - 3, half - 3), QPointF(-half - 5, half + 5))

        painter.setPen(QColor("#20262e"))
        font = painter.font()
        font.setBold(False)
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(QRectF(-34, 29, 68, 20), Qt.AlignmentFlag.AlignCenter, self.person.label)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._drag_start = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self._on_moved is not None and self.pos() != self._drag_start:
            self._on_moved(self, self._drag_start, self.pos())

    def refresh(self) -> None:
        self.setToolTip(self.person.label)
        self.update()


class RelationshipItem(QGraphicsLineItem):
    """Relationship line kept behind the individuals it connects."""

    def __init__(
        self, relationship: Relationship, member_a: IndividualItem, member_b: IndividualItem
    ) -> None:
        super().__init__()
        self.relationship = relationship
        self.member_a = member_a
        self.member_b = member_b
        self.setPen(QPen(QColor("#303740"), 2))
        self.setZValue(-10)
        self.update_position()

    def update_position(self) -> None:
        center_line = QLineF(self.member_a.pos(), self.member_b.pos())
        length = center_line.length()
        inset = SYMBOL_SIZE / 2
        if length <= inset * 2:
            self.setLine(center_line)
            return
        unit_x = center_line.dx() / length
        unit_y = center_line.dy() / length
        start = center_line.p1() + QPointF(unit_x * inset, unit_y * inset)
        end = center_line.p2() - QPointF(unit_x * inset, unit_y * inset)
        self.setLine(QLineF(start, end))

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        if self.relationship.kind != RelationshipKind.CONSANGUINEOUS_PARTNERSHIP:
            super().paint(painter, option, widget)
            return
        line = self.line()
        normal = line.normalVector()
        normal.setLength(4)
        offset = normal.p2() - normal.p1()
        painter.setPen(self.pen())
        painter.drawLine(line.translated(offset))
        painter.drawLine(line.translated(-offset))
