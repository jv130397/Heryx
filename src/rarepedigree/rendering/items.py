"""Qt graphics items implementing the confirmed basic pedigree symbols."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QCoreApplication, QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsSceneContextMenuEvent,
    QGraphicsSceneMouseEvent,
    QMenu,
    QStyleOptionGraphicsItem,
    QWidget,
)

from rarepedigree.domain import (
    GenderIdentity,
    Individual,
    ObservationStatus,
    Parentage,
    ParentageKind,
    Relationship,
    RelationshipKind,
    TwinGroup,
    TwinZygosity,
)
from rarepedigree.rendering.style import PedigreeRenderStyle

SYMBOL_SIZE = 48.0


class IndividualItem(QGraphicsObject):
    """Movable symbol whose geometry is derived from, but does not mutate, clinical data."""

    def __init__(
        self,
        person: Individual,
        on_moved: Callable[[IndividualItem, QPointF, QPointF], None] | None = None,
        on_context_action: Callable[[IndividualItem, str], None] | None = None,
        context_actions: Callable[[IndividualItem], set[str]] | None = None,
        render_style: PedigreeRenderStyle | None = None,
    ) -> None:
        super().__init__()
        self.person = person
        self._on_moved = on_moved
        self._on_context_action = on_context_action
        self._context_actions = context_actions
        self._drag_start = QPointF()
        self.render_style = render_style or PedigreeRenderStyle()
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setPos(person.layout.x, person.layout.y)
        self.setToolTip(person.label)
        self.adopted = False

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
        normal_color = self.render_style.category_color(self.person.gender_identity)
        pen = QPen(QColor("#22D3EE") if selected else QColor(normal_color), 4 if selected else 3)
        if self.person.placeholder:
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        status = self.person.phenotype_status
        brush_color = (
            QColor("#20262e") if status == ObservationStatus.PRESENT else QColor("#ffffff")
        )
        painter.setBrush(QBrush(brush_color))
        painter.drawPath(self.shape())
        half = SYMBOL_SIZE / 2
        if self.adopted:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(QPointF(-half - 8, -half - 5), QPointF(-half - 8, half + 5))
            painter.drawLine(QPointF(-half - 8, -half - 5), QPointF(-half - 2, -half - 5))
            painter.drawLine(QPointF(-half - 8, half + 5), QPointF(-half - 2, half + 5))
            painter.drawLine(QPointF(half + 8, -half - 5), QPointF(half + 8, half + 5))
            painter.drawLine(QPointF(half + 2, -half - 5), QPointF(half + 8, -half - 5))
            painter.drawLine(QPointF(half + 2, half + 5), QPointF(half + 8, half + 5))

        if status == ObservationStatus.UNKNOWN:
            painter.setPen(QPen(QColor("#5b6573"), 2))
            font = painter.font()
            font.setBold(True)
            font.setPointSize(15)
            painter.setFont(font)
            painter.drawText(QRectF(-12, -15, 24, 30), Qt.AlignmentFlag.AlignCenter, "?")

        painter.setPen(QPen(QColor("#20262e"), 2))
        if self.person.deceased:
            painter.drawLine(QPointF(-half - 5, half + 5), QPointF(half + 5, -half - 5))
        if self.person.proband or self.person.consultand:
            painter.drawLine(QPointF(-half - 22, half + 14), QPointF(-half - 3, half - 3))
            painter.drawLine(QPointF(-half - 3, half - 3), QPointF(-half - 10, half - 1))
            painter.drawLine(QPointF(-half - 3, half - 3), QPointF(-half - 5, half + 5))
            if self.person.proband and self.person.consultand:
                role = "P/C"
            else:
                role = "P" if self.person.proband else "C"
            painter.drawText(
                QRectF(-half - 30, half + 8, 24, 16), Qt.AlignmentFlag.AlignCenter, role
            )

        painter.setPen(QColor("#20262e"))
        font = painter.font()
        font.setBold(False)
        font.setPointSize(self.render_style.identifier_size)
        painter.setFont(font)
        painter.drawText(QRectF(-34, 29, 68, 20), Qt.AlignmentFlag.AlignCenter, self.person.label)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._drag_start = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        if self._on_moved is not None and self.pos() != self._drag_start:
            self._on_moved(self, self._drag_start, self.pos())

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._on_context_action is not None:
            self._on_context_action(self, "edit_dialog")
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def refresh(self) -> None:
        self.setToolTip(self.person.label)
        self.update()

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        if self._on_context_action is None:
            return super().contextMenuEvent(event)
        menu, actions = self.build_context_menu()
        selected = menu.exec(event.screenPos())
        if selected in actions:
            self._on_context_action(self, actions[selected])

    def build_context_menu(self) -> tuple[QMenu, dict]:
        """Build the same semantically filtered menu used by the real popup event."""
        allowed = self._context_actions(self) if self._context_actions else {
            "father", "mother", "unknown_parents", "partner", "child",
            "adopted_child", "sibling", "edit_dialog", "edit", "delete",
        }
        menu = QMenu()
        actions = {}
        entries = [
            ("□  Adicionar pai", "father"), ("○  Adicionar mãe", "mother"),
            ("Adicionar pais desconhecidos", "unknown_parents"),
            ("◇  Adicionar parceiro", "partner"), ("○  Adicionar filho", "child"),
            ("Adicionar filho adotivo", "adopted_child"),
            ("□  Adicionar irmão", "sibling"),
        ]
        for label, key in entries:
            if key in allowed:
                actions[menu.addAction(QCoreApplication.translate("RarePedigree", label))] = key
        menu.addSeparator()
        for label, key in [("✎  Editar indivíduo", "edit_dialog"),
                           ("Abrir propriedades", "edit"),
                           ("⌫  Excluir indivíduo", "delete")]:
            if key in allowed:
                actions[menu.addAction(QCoreApplication.translate("RarePedigree", label))] = key
        return menu, actions


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
            if self.relationship.kind in {
                RelationshipKind.SEPARATED_PARTNERSHIP,
                RelationshipKind.DIVORCED_PARTNERSHIP,
            }:
                midpoint = self.line().center()
                painter.setPen(self.pen())
                painter.drawLine(midpoint + QPointF(-5, 10), midpoint + QPointF(5, -10))
                if self.relationship.kind == RelationshipKind.DIVORCED_PARTNERSHIP:
                    painter.drawLine(midpoint + QPointF(2, 10), midpoint + QPointF(12, -10))
            return
        line = self.line()
        normal = line.normalVector()
        normal.setLength(4)
        offset = normal.p2() - normal.p1()
        painter.setPen(self.pen())
        painter.drawLine(line.translated(offset))
        painter.drawLine(line.translated(-offset))


class ParentageConnectorItem(QGraphicsPathItem):
    """Elbow connector from one or more explicit parents to a child."""

    def __init__(
        self,
        edges: list[Parentage],
        parents: list[IndividualItem],
        child: IndividualItem,
    ) -> None:
        super().__init__()
        self.edges = edges
        self.parents = parents
        self.child = child
        pen = QPen(QColor("#303740"), 2)
        if any(edge.kind != ParentageKind.BIOLOGICAL for edge in edges):
            pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
        self.setZValue(-9)
        self.update_position()

    def update_position(self) -> None:
        if not self.parents:
            return
        parent_x = sum(item.pos().x() for item in self.parents) / len(self.parents)
        parent_y = max(item.pos().y() for item in self.parents) + SYMBOL_SIZE / 2
        child_x = self.child.pos().x()
        child_y = self.child.pos().y() - SYMBOL_SIZE / 2
        junction_y = parent_y + max(35.0, (child_y - parent_y) * 0.5)
        path = QPainterPath(QPointF(parent_x, parent_y))
        path.lineTo(parent_x, junction_y)
        path.lineTo(child_x, junction_y)
        path.lineTo(child_x, child_y)
        self.setPath(path)


class TwinConnectorItem(QGraphicsPathItem):
    def __init__(
        self, group: TwinGroup, parents: list[IndividualItem], children: list[IndividualItem]
    ) -> None:
        super().__init__()
        self.group = group
        self.parents = parents
        self.children = children
        self.setPen(QPen(QColor("#303740"), 2))
        self.setZValue(-8)
        self.update_position()

    def update_position(self) -> None:
        if not self.parents or len(self.children) < 2:
            return
        parent_x = sum(item.pos().x() for item in self.parents) / len(self.parents)
        parent_y = max(item.pos().y() for item in self.parents) + SYMBOL_SIZE / 2
        child_top = min(item.pos().y() for item in self.children) - SYMBOL_SIZE / 2
        junction = QPointF(parent_x, parent_y + max(35.0, (child_top - parent_y) * 0.5))
        path = QPainterPath(QPointF(parent_x, parent_y))
        path.lineTo(junction)
        for child in self.children:
            path.moveTo(junction)
            path.lineTo(QPointF(child.pos().x(), child.pos().y() - SYMBOL_SIZE / 2))
        if self.group.zygosity == TwinZygosity.MONOZYGOTIC:
            left, right = sorted(self.children, key=lambda item: item.pos().x())[:2]
            left_mid = QPointF(
                (junction.x() + left.pos().x()) / 2,
                (junction.y() + left.pos().y() - SYMBOL_SIZE / 2) / 2,
            )
            right_mid = QPointF(
                (junction.x() + right.pos().x()) / 2,
                (junction.y() + right.pos().y() - SYMBOL_SIZE / 2) / 2,
            )
            path.moveTo(left_mid)
            path.lineTo(right_mid)
        self.setPath(path)
