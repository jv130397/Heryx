"""Single Python source of truth exposed to the Genomic Nexus QML prototype."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, QSettings, Signal, Slot
from PySide6.QtGui import QUndoCommand, QUndoStack

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    ObservationStatus,
    PedigreeProject,
)
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.rendering.style import PedigreeRenderStyle
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui_next.bridge.people_model import PeopleModel


class _UpdatePersonCommand(QUndoCommand):
    def __init__(
        self, person: Individual, old: dict[str, Any], new: dict[str, Any], callback
    ) -> None:
        super().__init__("Editar indivíduo")
        self.person, self.old, self.new, self.callback = person, old, new, callback

    def _apply(self, values: dict[str, Any]) -> None:
        for field, value in values.items():
            setattr(self.person, field, value)
        self.callback()

    def redo(self) -> None:
        self._apply(self.new)

    def undo(self) -> None:
        self._apply(self.old)


class NexusController(QObject):
    projectChanged = Signal()
    selectionChanged = Signal()
    languageChanged = Signal()
    styleChanged = Signal()
    undoStateChanged = Signal()

    def __init__(self, project: PedigreeProject | None = None, parent=None) -> None:
        super().__init__(parent)
        self.settings = QSettings()
        self.project = project or self.synthetic_project()
        self.style = PedigreeRenderStyle.from_settings(self.settings)
        self.people_model = PeopleModel(self.project, self.style, self)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.canUndoChanged.connect(self.undoStateChanged)
        self.undo_stack.canRedoChanged.connect(self.undoStateChanged)
        self._selected_id = str(self.project.individuals[0].id) if self.project.individuals else ""
        self.people_model.set_selected(self._selected_id)
        language_manager.languageChanged.connect(self._on_language_changed)

    @staticmethod
    def synthetic_project() -> PedigreeProject:
        project = PedigreeProject(title="Família Nexus", family={"label": "SYN-NEXUS"})
        focus = Individual(label="II-1", gender_identity=GenderIdentity.WOMAN)
        project.individuals.append(focus)
        project, _ = FamilyService.add_parents(project, focus.id)
        project, partner_id = FamilyService.add_partner(project, focus.id)
        project, _ = FamilyService.add_child(project, focus.id, partner_id)
        positions = PedigreeLayoutEngine().compute(project)
        for person in project.individuals:
            person.layout.x, person.layout.y = positions[person.id]
        final_focus = next(person for person in project.individuals if person.id == focus.id)
        final_focus.phenotype_status = ObservationStatus.PRESENT
        final_focus.proband = True
        return project

    @Slot(str)
    def _on_language_changed(self, _language: str) -> None:
        self.languageChanged.emit()

    @Property(QObject, constant=True)
    def peopleModel(self):
        return self.people_model

    @Property(str, notify=projectChanged)
    def projectName(self) -> str:
        return self.project.title

    @Property(int, notify=projectChanged)
    def personCount(self) -> int:
        return len(self.project.individuals)

    @Property(int, notify=projectChanged)
    def generationCount(self) -> int:
        values = PedigreeLayoutEngine().generations(self.project).values()
        return len(set(values)) if values else 0

    @Property(str, notify=selectionChanged)
    def selectedId(self) -> str:
        return self._selected_id

    @Property("QVariantMap", notify=selectionChanged)
    def selectedPerson(self) -> dict[str, Any]:
        if not self._selected_id:
            return {}
        person = self.people_model.person(self._selected_id)
        return {
            "id": str(person.id), "label": person.label,
            "gender": person.gender_identity.value,
            "phenotype": person.phenotype_status.value,
            "deceased": person.deceased, "proband": person.proband,
        }

    @Property("QVariantList", notify=projectChanged)
    def connectors(self) -> list[dict[str, Any]]:
        people = {person.id: person for person in self.project.individuals}
        result = []
        for relation in self.project.relationships:
            a, b = people[relation.member_a], people[relation.member_b]
            result.append({"x1": a.layout.x, "y1": a.layout.y,
                           "x2": b.layout.x, "y2": b.layout.y, "kind": "partner"})
        for edge in self.project.parentages:
            a, b = people[edge.parent_id], people[edge.child_id]
            result.append({"x1": a.layout.x, "y1": a.layout.y,
                           "x2": b.layout.x, "y2": b.layout.y, "kind": "parent"})
        return result

    @Property(bool, notify=undoStateChanged)
    def canUndo(self) -> bool:
        return self.undo_stack.canUndo()

    @Property(bool, notify=undoStateChanged)
    def canRedo(self) -> bool:
        return self.undo_stack.canRedo()

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return language_manager.language

    @Slot(str)
    def selectPerson(self, person_id: str) -> None:
        self._selected_id = person_id
        self.people_model.set_selected(person_id)
        self.selectionChanged.emit()

    @Slot(str, str, bool)
    def updateSelected(self, label: str, phenotype: str, deceased: bool) -> None:
        if not self._selected_id:
            return
        person = self.people_model.person(self._selected_id)
        new = {"label": label.strip() or person.label,
               "phenotype_status": ObservationStatus(phenotype), "deceased": deceased}
        old = {key: getattr(person, key) for key in new}
        if old != new:
            self.undo_stack.push(_UpdatePersonCommand(person, old, new, self._refresh_person))

    def _refresh_person(self) -> None:
        self.people_model.refresh()
        self.selectionChanged.emit()
        self.projectChanged.emit()

    @Slot()
    def undo(self) -> None:
        self.undo_stack.undo()

    @Slot()
    def redo(self) -> None:
        self.undo_stack.redo()

    @Slot(str)
    def setLanguage(self, language: str) -> None:
        language_manager.set_language(language)

    @Slot(str, result=str)
    def translate(self, source: str) -> str:
        translations = {
            "en": {"Selecionar": "Select", "Adicionar indivíduo": "Add individual",
                   "Adicionar familiar": "Add relative", "Relacionamentos": "Relationships",
                   "Mover": "Move", "Excluir": "Delete", "Propriedades": "Properties",
                   "Identificação": "Identity", "Fenótipo": "Phenotype",
                   "Confirmar": "Confirm", "Cancelar": "Cancel", "Preferências": "Preferences",
                   "indivíduos": "individuals", "gerações": "generations",
                   "Projeto atualizado": "Project updated", "Editar indivíduo": "Edit individual",
                   "Desconhecido": "Unknown", "Afetado": "Affected",
                   "Não afetado": "Unaffected", "Falecido": "Deceased",
                   "Cores de representação": "Representation colors",
                   "Modo científico monocromático": "Scientific monochrome mode",
                   "Exportar": "Export", "Clínica": "Clinical",
                   "Relações": "Relations"}
        }
        return translations.get(language_manager.language, {}).get(source, source)

    @Slot(str, str, str, bool)
    def setColors(self, man: str, woman: str, unspecified: str, monochrome: bool) -> None:
        self.style.man_color, self.style.woman_color = man, woman
        self.style.unspecified_color, self.style.monochrome = unspecified, monochrome
        for key, value in {
            "pedigree/man_color": man, "pedigree/woman_color": woman,
            "pedigree/unspecified_color": unspecified, "pedigree/monochrome": monochrome,
        }.items():
            self.settings.setValue(key, value)
        self.people_model.style = self.style
        self.people_model.refresh()
        self.styleChanged.emit()
