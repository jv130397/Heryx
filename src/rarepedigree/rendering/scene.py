"""Pedigree scene mapping domain identifiers to graphics items."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsScene

from rarepedigree.domain import Individual, PedigreeProject, Relationship
from rarepedigree.rendering.items import IndividualItem, RelationshipItem


class PedigreeScene(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__(QRectF(-2000, -1400, 4000, 2800))
        self.setBackgroundBrush(QColor("#f7f9fb"))
        self.person_items: dict[UUID, IndividualItem] = {}
        self.relationship_items: dict[UUID, RelationshipItem] = {}
        self.on_person_moved: Callable[[IndividualItem, QPointF, QPointF], None] | None = None

    def load_project(self, project: PedigreeProject) -> None:
        self.clear()
        self.person_items.clear()
        self.relationship_items.clear()
        for person in project.individuals:
            self.add_person(person)
        for relationship in project.relationships:
            self.add_relationship(relationship)

    def add_person(self, person: Individual) -> IndividualItem:
        item = IndividualItem(person, self._person_moved)
        self.addItem(item)
        self.person_items[person.id] = item
        return item

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

    def selected_people(self) -> list[IndividualItem]:
        return [item for item in self.selectedItems() if isinstance(item, IndividualItem)]

