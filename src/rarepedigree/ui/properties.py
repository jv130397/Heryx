"""Properties editor for a selected individual."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.domain import GenderIdentity, ObservationStatus
from rarepedigree.rendering import IndividualItem


class PropertiesPanel(QWidget):
    def __init__(self, on_apply: Callable[[IndividualItem, dict[str, Any]], None]) -> None:
        super().__init__()
        self._item: IndividualItem | None = None
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

        tabs = QTabWidget()
        identity = QWidget()
        form = QFormLayout(identity)
        form.addRow("Identificador exibido", self.label_edit)
        form.addRow("Símbolo/gênero", self.gender_combo)
        form.addRow("Estado fenotípico", self.phenotype_combo)
        form.addRow(self.deceased_check)
        form.addRow(self.proband_check)
        form.addRow(self.consultand_check)
        form.addRow(self.lock_layout_check)
        form.addRow(self.apply_button)
        tabs.addTab(identity, "Identificação")
        relations = QLabel("Relações familiares são editadas pelo canvas e menu contextual.")
        relations.setWordWrap(True)
        tabs.addTab(relations, "Relações")
        clinical = QLabel("Campos HPO e variantes reservados para a Fase 5.")
        clinical.setWordWrap(True)
        tabs.addTab(clinical, "Clínica")
        root = QVBoxLayout(self)
        root.addWidget(tabs)
        self.setEnabled(False)

    def set_item(self, item: IndividualItem | None) -> None:
        self._item = item
        self.setEnabled(item is not None)
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
