"""Undoable commands connecting the domain project to the scene."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF
from PySide6.QtGui import QUndoCommand

from rarepedigree.domain import Individual, PedigreeProject, Relationship
from rarepedigree.rendering import IndividualItem, PedigreeScene


class AddIndividualCommand(QUndoCommand):
    def __init__(self, project: PedigreeProject, scene: PedigreeScene, person: Individual) -> None:
        super().__init__("Adicionar indivíduo")
        self.project = project
        self.scene = scene
        self.person = person

    def redo(self) -> None:
        if not any(person.id == self.person.id for person in self.project.individuals):
            self.project.individuals.append(self.person)
        if self.person.id not in self.scene.person_items:
            self.scene.add_person(self.person)

    def undo(self) -> None:
        self.project.individuals = [p for p in self.project.individuals if p.id != self.person.id]
        self.scene.remove_person(self.person.id)


class AddRelationshipCommand(QUndoCommand):
    def __init__(
        self, project: PedigreeProject, scene: PedigreeScene, relationship: Relationship
    ) -> None:
        super().__init__("Adicionar relação")
        self.project = project
        self.scene = scene
        self.relationship = relationship

    def redo(self) -> None:
        if not any(item.id == self.relationship.id for item in self.project.relationships):
            self.project.relationships.append(self.relationship)
        if self.relationship.id not in self.scene.relationship_items:
            self.scene.add_relationship(self.relationship)

    def undo(self) -> None:
        self.project.relationships = [
            item for item in self.project.relationships if item.id != self.relationship.id
        ]
        self.scene.remove_relationship(self.relationship.id)


class MoveIndividualCommand(QUndoCommand):
    def __init__(
        self,
        scene: PedigreeScene,
        item: IndividualItem,
        old_position: QPointF,
        new_position: QPointF,
    ) -> None:
        super().__init__("Mover indivíduo")
        self.scene = scene
        self.item = item
        self.old_position = old_position
        self.new_position = new_position
        self._first_redo = True

    def _apply(self, position: QPointF) -> None:
        self.item.setPos(position)
        self.item.person.layout.x = position.x()
        self.item.person.layout.y = position.y()
        self.scene.update_relationships(self.item.person.id)

    def redo(self) -> None:
        if self._first_redo:
            self._first_redo = False
            self.item.person.layout.x = self.new_position.x()
            self.item.person.layout.y = self.new_position.y()
            return
        self._apply(self.new_position)

    def undo(self) -> None:
        self._apply(self.old_position)


class UpdateIndividualCommand(QUndoCommand):
    def __init__(
        self,
        item: IndividualItem,
        old_values: dict[str, Any],
        new_values: dict[str, Any],
    ) -> None:
        super().__init__("Editar indivíduo")
        self.item = item
        self.old_values = old_values
        self.new_values = new_values

    def _apply(self, values: dict[str, Any]) -> None:
        for field, value in values.items():
            setattr(self.item.person, field, value)
        self.item.refresh()

    def redo(self) -> None:
        self._apply(self.new_values)

    def undo(self) -> None:
        self._apply(self.old_values)

