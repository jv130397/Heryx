"""Properties editor for a selected individual."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.domain import GenderIdentity, ObservationStatus, PedigreeProject
from rarepedigree.rendering import IndividualItem
from rarepedigree.ui.components import SectionHeader


class PropertiesPanel(QWidget):
    def __init__(self, on_apply: Callable[[IndividualItem, dict[str, Any]], None]) -> None:
        super().__init__()
        self._item: IndividualItem | None = None
        self._project: PedigreeProject | None = None
        self._on_apply = on_apply
        self.label_edit = QLineEdit()
        self.gender_combo = QComboBox()
        for label, value in (
            ("Homem/menino", GenderIdentity.MAN),
            ("Mulher/menina", GenderIdentity.WOMAN),
            ("Gênero diverso", GenderIdentity.GENDER_DIVERSE),
            ("Não conhecido/especificado", GenderIdentity.UNKNOWN),
        ):
            self.gender_combo.addItem(label, value)
        self.phenotype_combo = QComboBox()
        for label, value in (
            ("Desconhecido", ObservationStatus.UNKNOWN),
            ("Clinicamente afetado", ObservationStatus.PRESENT),
            ("Explicitamente não afetado", ObservationStatus.ABSENT),
        ):
            self.phenotype_combo.addItem(label, value)
        self.deceased_check = QCheckBox("Falecido")
        self.proband_check = QCheckBox("Proband")
        self.consultand_check = QCheckBox("Consultand")
        self.lock_layout_check = QCheckBox("Preservar posição no auto-layout")
        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self._apply)

        self.tabs = QTabWidget()
        identity = QWidget()
        form = QFormLayout(identity)
        form.setContentsMargins(14, 16, 14, 16)
        form.setSpacing(10)
        form.addRow(SectionHeader("Identificação"))
        form.addRow("Identificador exibido", self.label_edit)
        form.addRow("Símbolo/gênero", self.gender_combo)
        form.addRow("Estado fenotípico", self.phenotype_combo)
        form.addRow(self.deceased_check)
        form.addRow(self.proband_check)
        form.addRow(self.consultand_check)
        form.addRow(self.lock_layout_check)
        form.addRow(self.apply_button)
        self.tabs.addTab(identity, "Identificação")
        relations = QWidget()
        relation_layout = QVBoxLayout(relations)
        relation_layout.setContentsMargins(14, 16, 14, 16)
        relation_layout.addWidget(SectionHeader("Relações calculadas"))
        self.parents_label = QLabel()
        self.partners_label = QLabel()
        self.children_label = QLabel()
        for widget in (self.parents_label, self.partners_label, self.children_label):
            widget.setWordWrap(True)
            relation_layout.addWidget(widget)
        relation_layout.addStretch()
        self.tabs.addTab(relations, "Relações")
        clinical = QLabel("Campos HPO e variantes reservados para a Fase 5.")
        clinical.setWordWrap(True)
        clinical.setMargin(16)
        self.tabs.addTab(clinical, "Clínica")
        self.empty = QLabel("Selecione um indivíduo para consultar ou editar suas propriedades.")
        self.empty.setWordWrap(True)
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty.setMargin(28)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.tabs)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.stack)
        self.stack.setCurrentWidget(self.empty)

    def set_item(
        self, item: IndividualItem | None, project: PedigreeProject | None = None
    ) -> None:
        self._item = item
        self._project = project
        self.stack.setCurrentWidget(self.tabs if item is not None else self.empty)
        if item is None:
            return
        person = item.person
        self.label_edit.setText(person.label)
        self._select_data(self.gender_combo, person.gender_identity)
        self._select_data(self.phenotype_combo, person.phenotype_status)
        self.deceased_check.setChecked(person.deceased)
        self.proband_check.setChecked(person.proband)
        self.consultand_check.setChecked(person.consultand)
        self.lock_layout_check.setChecked(person.layout.locked)
        self._update_relations(person.id)

    def _update_relations(self, person_id) -> None:
        if self._project is None:
            return
        names = {person.id: person.label for person in self._project.individuals}
        parents = [
            names[edge.parent_id]
            for edge in self._project.parentages
            if edge.child_id == person_id
        ]
        children = [
            names[edge.child_id]
            for edge in self._project.parentages
            if edge.parent_id == person_id
        ]
        partners = [
            names[relation.member_b if relation.member_a == person_id else relation.member_a]
            for relation in self._project.relationships
            if person_id in {relation.member_a, relation.member_b}
        ]
        self.parents_label.setText(f"Pais: {', '.join(parents) if parents else 'não registrados'}")
        partner_text = ", ".join(partners) if partners else "não registrados"
        child_text = ", ".join(children) if children else "não registrados"
        self.partners_label.setText(f"Parceiros: {partner_text}")
        self.children_label.setText(f"Filhos: {child_text}")

    @staticmethod
    def _select_data(combo: QComboBox, value: object) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _apply(self) -> None:
        if self._item is None:
            return
        self._on_apply(
            self._item,
            {
                "label": self.label_edit.text().strip() or "Indivíduo",
                "gender_identity": self.gender_combo.currentData(),
                "phenotype_status": self.phenotype_combo.currentData(),
                "deceased": self.deceased_check.isChecked(),
                "proband": self.proband_check.isChecked(),
                "consultand": self.consultand_check.isChecked(),
                "layout": self._item.person.layout.model_copy(
                    update={"locked": self.lock_layout_check.isChecked()}
                ),
            },
        )
