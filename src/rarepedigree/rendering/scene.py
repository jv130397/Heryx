"""Pedigree scene mapping domain identifiers to graphics items."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from PySide6.QtCore import QCoreApplication, QPointF, QRectF
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsSimpleTextItem

from rarepedigree.domain import Individual, ParentageKind, PedigreeProject, Relationship
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.rendering.items import (
    IndividualItem,
    ParentageConnectorItem,
    RelationshipItem,
    TwinConnectorItem,
)
from rarepedigree.rendering.style import PedigreeRenderStyle


class PedigreeScene(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__(QRectF(-2000, -1400, 4000, 2800))
        self.setBackgroundBrush(QColor("#f7f9fb"))
        self.person_items: dict[UUID, IndividualItem] = {}
        self.relationship_items: dict[UUID, RelationshipItem] = {}
        self.parentage_items: dict[UUID, ParentageConnectorItem] = {}
        self.twin_items: dict[UUID, TwinConnectorItem] = {}
        self.generation_items: list[QGraphicsSimpleTextItem] = []
        self.legend_item: QGraphicsSimpleTextItem | None = None
        self.project = PedigreeProject()
        self.render_style = PedigreeRenderStyle.from_settings()
        self.on_person_moved: Callable[[IndividualItem, QPointF, QPointF], None] | None = None
        self.on_context_action: Callable[[IndividualItem, str], None] | None = None
        self.context_actions: Callable[[IndividualItem], set[str]] | None = None
        self.interaction_mode = "select"

    def load_project(self, project: PedigreeProject) -> None:
        self.clear()
        self.project = project
        self.person_items.clear()
        self.relationship_items.clear()
        self.parentage_items.clear()
        self.twin_items.clear()
        self.generation_items.clear()
        self.legend_item = None
        for person in project.individuals:
            self.add_person(person)
        for edge in project.parentages:
            if edge.kind == ParentageKind.LEGAL:
                self.person_items[edge.child_id].adopted = True
        for relationship in project.relationships:
            self.add_relationship(relationship)
        self._add_parentage_connectors(project)
        self._add_generation_labels(project)
        self._add_legend()

    def _add_generation_labels(self, project: PedigreeProject) -> None:
        generations = PedigreeLayoutEngine().generations(project)
        if not self.person_items:
            return
        label_x = min(item.pos().x() for item in self.person_items.values()) - 110
        for generation in sorted(set(generations.values())):
            members = [
                self.person_items[item]
                for item, value in generations.items()
                if value == generation
            ]
            if not members:
                continue
            label = QGraphicsSimpleTextItem(_roman(generation + 1))
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            label.setFont(font)
            label.setBrush(QColor("#516575"))
            label.setPos(label_x, members[0].pos().y() - 12)
            self.addItem(label)
            self.generation_items.append(label)

    def _add_legend(self) -> None:
        bounds = self.itemsBoundingRect()

        def translate(text: str) -> str:
            return QCoreApplication.translate("RarePedigree", text)

        category = (
            "  |  " + translate("contorno azul/rosa/cinza = categoria de representação")
            if self.render_style.category_colors and not self.render_style.monochrome
            else "  |  " + translate("modo científico monocromático")
        )
        legend = QGraphicsSimpleTextItem(
            translate("Legenda: preenchido = afetado")
            + "  |  ? = "
            + translate("estado desconhecido")
            + "  |  / = "
            + translate("falecido")
            + "  |  P = proband  |  C = consultand"
            + category
        )
        legend.setBrush(QColor("#344b5a"))
        positions = {
            "top": (bounds.left(), bounds.top() - 45),
            "right": (bounds.right() + 45, bounds.top()),
            "bottom": (bounds.left(), bounds.bottom() + 45),
        }
        legend.setPos(*positions.get(self.render_style.legend_position, positions["bottom"]))
        self.addItem(legend)
        self.legend_item = legend
        # The interactive canvas deliberately stays free of a legend because
        # its wide bounding box distorts fit-to-view. Exporters may temporarily
        # reveal the same item when the export option requests it.
        legend.setVisible(False)

    def _add_parentage_connectors(self, project: PedigreeProject) -> None:
        twin_member_ids = {member for group in project.twin_groups for member in group.member_ids}
        child_ids = {edge.child_id for edge in project.parentages} - twin_member_ids
        children_by_parents: dict[frozenset[UUID], list[UUID]] = {}
        relationship_pairs = {
            frozenset((relation.member_a, relation.member_b)) for relation in project.relationships
        }
        for child_id in child_ids:
            parent_ids = frozenset(
                edge.parent_id for edge in project.parentages if edge.child_id == child_id
            )
            children_by_parents.setdefault(parent_ids, []).append(child_id)
        generations = PedigreeLayoutEngine().generations(project)
        groups_by_generation: dict[int, list[frozenset[UUID]]] = {}
        for parent_ids, grouped_children in children_by_parents.items():
            generation = generations[grouped_children[0]]
            groups_by_generation.setdefault(generation, []).append(parent_ids)
        offsets: dict[frozenset[UUID], float] = {}
        for parent_sets in groups_by_generation.values():
            frequencies: dict[UUID, int] = {}
            for parent_ids in parent_sets:
                for parent_id in parent_ids:
                    frequencies[parent_id] = frequencies.get(parent_id, 0) + 1
            shared_nuclei = [
                parent_ids
                for parent_ids in parent_sets
                if any(frequencies[parent_id] > 1 for parent_id in parent_ids)
            ]
            shared_nuclei.sort(
                key=lambda ids: sum(self.person_items[item].pos().x() for item in ids)
                / max(1, len(ids))
            )
            # A shared parent with multiple co-parents cannot use a straight
            # same-level line to a distant partner: it would cross the
            # intervening partners. Route every such nucleus below identifiers
            # on a dedicated orthogonal lane. Independent nuclei stay natural.
            for parent_ids in parent_sets:
                offsets[parent_ids] = 0.0
            independent = [item for item in parent_sets if item not in shared_nuclei]
            intervals = []
            for parent_ids in independent:
                points = [self.person_items[item].pos().x() for item in parent_ids]
                points.extend(
                    self.person_items[child_id].pos().x()
                    for child_id in children_by_parents[parent_ids]
                )
                intervals.append((min(points), max(points), parent_ids))
            active: list[tuple[float, int]] = []
            for left, right, parent_ids in sorted(intervals, key=lambda item: item[0]):
                active = [(end, lane) for end, lane in active if left <= end + 8.0]
                lane = max((item[1] for item in active), default=-1) + 1
                active.append((right, lane))
                offsets[parent_ids] = lane * 14.0
            for index, parent_ids in enumerate(shared_nuclei):
                offsets[parent_ids] = 68.0 + index * 14.0
        for parent_ids, grouped_children in children_by_parents.items():
            edges = [edge for edge in project.parentages if edge.child_id in grouped_children]
            parents = [self.person_items[parent_id] for parent_id in parent_ids]
            children = [self.person_items[child_id] for child_id in grouped_children]
            item = ParentageConnectorItem(
                edges,
                parents,
                children,
                draw_coparent_line=len(parent_ids) == 2 and parent_ids not in relationship_pairs,
                routing_offset=offsets[parent_ids],
            )
            self.addItem(item)
            for child_id in grouped_children:
                self.parentage_items[child_id] = item
        for group in project.twin_groups:
            edges = [edge for edge in project.parentages if edge.child_id == group.member_ids[0]]
            parents = [self.person_items[edge.parent_id] for edge in edges]
            children = [self.person_items[member_id] for member_id in group.member_ids]
            item = TwinConnectorItem(group, parents, children)
            self.addItem(item)
            self.twin_items[group.id] = item

    def add_person(self, person: Individual) -> IndividualItem:
        item = IndividualItem(
            person,
            self._person_moved,
            self.on_context_action,
            self.context_actions,
            self.render_style,
        )
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, self.interaction_mode == "move")
        self.addItem(item)
        self.person_items[person.id] = item
        return item

    def set_interaction_mode(self, mode: str) -> None:
        if mode not in {"select", "move"}:
            raise ValueError(f"Unknown interaction mode: {mode}")
        self.interaction_mode = mode
        for item in self.person_items.values():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, mode == "move")

    def apply_render_style(self, style: PedigreeRenderStyle) -> None:
        selected_ids = {item.person.id for item in self.selected_people()}
        self.render_style = style
        self.load_project(self.project)
        for person_id in selected_ids:
            if person_id in self.person_items:
                self.person_items[person_id].setSelected(True)

    def remove_person(self, person_id: UUID) -> None:
        item = self.person_items.pop(person_id)
        self.removeItem(item)

    def add_relationship(self, relationship: Relationship) -> RelationshipItem:
        item = RelationshipItem(
            relationship,
            self.person_items[relationship.member_a],
            self.person_items[relationship.member_b],
        )
        self.addItem(item)
        self.relationship_items[relationship.id] = item
        return item

    def remove_relationship(self, relationship_id: UUID) -> None:
        item = self.relationship_items.pop(relationship_id)
        self.removeItem(item)

    def _person_moved(self, item: IndividualItem, old: QPointF, new: QPointF) -> None:
        self.update_relationships(item.person.id)
        if self.on_person_moved is not None:
            self.on_person_moved(item, old, new)

    def update_relationships(self, person_id: UUID) -> None:
        for item in self.relationship_items.values():
            relation = item.relationship
            if person_id in {relation.member_a, relation.member_b}:
                item.update_position()
        for child_id, item in self.parentage_items.items():
            if person_id == child_id or any(edge.parent_id == person_id for edge in item.edges):
                item.update_position()
        for item in self.twin_items.values():
            if any(child.person.id == person_id for child in item.children) or any(
                parent.person.id == person_id for parent in item.parents
            ):
                item.update_position()

    def selected_people(self) -> list[IndividualItem]:
        return [item for item in self.selectedItems() if isinstance(item, IndividualItem)]

    def pedigree_bounding_rect(self) -> QRectF:
        """Bounds for editor navigation, explicitly excluding the export legend."""
        bounds = QRectF()
        for item in self.items():
            if item is not self.legend_item and item.isVisible():
                bounds = bounds.united(item.sceneBoundingRect())
        return bounds


def _roman(number: int) -> str:
    values = ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))
    result = ""
    for value, numeral in values:
        while number >= value:
            result += numeral
            number -= value
    return result
