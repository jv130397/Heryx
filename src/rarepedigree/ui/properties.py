"""Properties editor for a selected individual."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt, Signal
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

from rarepedigree.domain import (
    GenderIdentity,
    KinshipEngine,
    KinshipSeverity,
    ObservationStatus,
    ParentageKind,
    PedigreeProject,
    SiblingKind,
)
from rarepedigree.rendering import IndividualItem
from rarepedigree.rendering.items import ParentageConnectorItem
from rarepedigree.ui.components import SectionHeader
from rarepedigree.ui.i18n import tr


class PropertiesPanel(QWidget):
    editRequested = Signal()

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

        self.summary = QWidget()
        summary_layout = QVBoxLayout(self.summary)
        self.summary_symbol = QLabel("◇")
        self.summary_symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_symbol.setStyleSheet("font-size: 34px; color: #22D3EE;")
        self.summary_name = QLabel()
        self.summary_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_state = QLabel()
        self.summary_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit_button = QPushButton("Editar indivíduo")
        self.edit_button.clicked.connect(self.editRequested)
        summary_layout.addWidget(self.summary_symbol)
        summary_layout.addWidget(self.summary_name)
        summary_layout.addWidget(self.summary_state)
        summary_layout.addWidget(self.edit_button)
        self.tabs = QTabWidget()
        identity = QWidget()
        form = QFormLayout(identity)
        self.identity_form = form
        form.setContentsMargins(14, 16, 14, 16)
        form.setSpacing(10)
        self.identity_header = SectionHeader("Identificação")
        form.addRow(self.identity_header)
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
        self.relations_header = SectionHeader("Relações calculadas")
        relation_layout.addWidget(self.relations_header)
        self.parents_label = QLabel()
        self.kinship_label = QLabel()
        self.unknown_parents_label = QLabel()
        self.siblings_label = QLabel()
        self.partners_label = QLabel()
        self.children_label = QLabel()
        self.warnings_label = QLabel()
        for widget in (
            self.kinship_label,
            self.parents_label,
            self.unknown_parents_label,
            self.siblings_label,
            self.partners_label,
            self.children_label,
            self.warnings_label,
        ):
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
        root.addWidget(self.summary)
        root.addWidget(self.stack)
        self.stack.setCurrentWidget(self.empty)
        self.summary.setVisible(False)
        self.retranslate_ui()

    def set_item(self, item: IndividualItem | None, project: PedigreeProject | None = None) -> None:
        self._item = item
        self._project = project
        self.stack.setCurrentWidget(self.tabs if item is not None else self.empty)
        self.summary.setVisible(item is not None)
        if item is None:
            return
        person = item.person
        symbols = {
            GenderIdentity.MAN: "□",
            GenderIdentity.WOMAN: "○",
            GenderIdentity.GENDER_DIVERSE: "◇",
            GenderIdentity.UNKNOWN: "◇",
        }
        self.summary_symbol.setText(symbols[person.gender_identity])
        self.summary_name.setText(f"<b>{person.label}</b>")
        state_names = {
            ObservationStatus.PRESENT: tr("Afetado"),
            ObservationStatus.ABSENT: tr("Não afetado"),
            ObservationStatus.UNKNOWN: tr("Estado desconhecido"),
        }
        self.summary_state.setText(state_names[person.phenotype_status])
        self.label_edit.setText(person.label)
        self._select_data(self.gender_combo, person.gender_identity)
        self._select_data(self.phenotype_combo, person.phenotype_status)
        self.deceased_check.setChecked(person.deceased)
        self.proband_check.setChecked(person.proband)
        self.consultand_check.setChecked(person.consultand)
        self.lock_layout_check.setChecked(person.layout.locked)
        self._update_relations(person.id)

    def set_connection(self, item: ParentageConnectorItem) -> None:
        self._item = None
        self.summary.setVisible(False)
        parents = ", ".join(parent.person.label for parent in item.parents)
        children = ", ".join(child.person.label for child in item.children)
        edge_lines = [
            f"{edge.parent_id} → {edge.child_id} · {edge.kind.value} · {edge.evidence_status.value}"
            for edge in item.edges
        ]
        self.empty.setText(
            tr("Núcleo parental selecionado")
            + f"\n\n{tr('Genitores')}: {parents}\n{tr('Descendentes')}: {children}\n\n"
            + "\n".join(edge_lines)
        )
        self.stack.setCurrentWidget(self.empty)

    def _update_relations(self, person_id) -> None:
        if self._project is None:
            return
        names = {person.id: person.label for person in self._project.individuals}
        engine = KinshipEngine()
        parent_people = [
            person
            for person in self._project.individuals
            if person.id
            in engine.parents(self._project, person_id, {ParentageKind.BIOLOGICAL})
        ]
        parents = [person.label for person in parent_people if not person.placeholder]
        unknown_parents = [person.label for person in parent_people if person.placeholder]
        children = [
            names[edge.child_id] for edge in self._project.parentages if edge.parent_id == person_id
        ]
        partners = [
            names[relation.member_b if relation.member_a == person_id else relation.member_a]
            for relation in self._project.relationships
            if person_id in {relation.member_a, relation.member_b}
        ]
        self.parents_label.setText(f"Pais: {', '.join(parents) if parents else 'não registrados'}")
        self.unknown_parents_label.setText(
            "Genitores desconhecidos: "
            + (", ".join(unknown_parents) if unknown_parents else "nenhum")
        )
        full: list[str] = []
        half: list[str] = []
        for other in self._project.individuals:
            if other.id == person_id:
                continue
            kind = engine.sibling_kind(self._project, person_id, other.id)
            if kind == SiblingKind.FULL:
                full.append(other.label)
            elif kind in {SiblingKind.PATERNAL_HALF, SiblingKind.MATERNAL_HALF}:
                half.append(other.label)
        self.siblings_label.setText(
            f"Irmãos completos: {', '.join(full) if full else 'nenhum'}\n"
            f"Meio-irmãos: {', '.join(half) if half else 'nenhum'}"
        )
        partner_text = ", ".join(partners) if partners else "não registrados"
        child_text = ", ".join(children) if children else "não registrados"
        self.partners_label.setText(f"Parceiros: {partner_text}")
        self.children_label.setText(f"Filhos: {child_text}")
        probands = [person for person in self._project.individuals if person.proband]
        relationship = "não calculado"
        if len(probands) == 1:
            relationship = self._kinship_with_proband(engine, probands[0].id, person_id)
        self.kinship_label.setText(f"Parentesco com o probando: {relationship}")
        issues = [
            issue.message
            for issue in engine.validator.validate(self._project)
            if person_id in issue.person_ids
            and issue.severity in {KinshipSeverity.ERROR, KinshipSeverity.AMBIGUITY}
        ]
        self.warnings_label.setText(
            "Avisos: " + ("; ".join(issues) if issues else "nenhuma ambiguidade detectada")
        )

    def _kinship_with_proband(self, engine: KinshipEngine, proband_id, person_id) -> str:
        if person_id == proband_id:
            return "probando"
        parent_ids = engine.parents(self._project, proband_id, {ParentageKind.BIOLOGICAL})
        if person_id in parent_ids:
            return "genitor"
        if proband_id in engine.children(self._project, person_id, {ParentageKind.BIOLOGICAL}):
            return "genitor"
        sibling = engine.sibling_kind(self._project, proband_id, person_id)
        if sibling is not None:
            return sibling.value
        context = engine.collateral_context(self._project, proband_id, person_id)
        if context is not None:
            return context[0]
        ancestors = engine.ancestors(self._project, proband_id)
        descendants = engine.descendants(self._project, proband_id)
        if person_id in ancestors:
            return f"ascendente ({ancestors[person_id]} geração/ões)"
        if person_id in descendants:
            return f"descendente ({descendants[person_id]} geração/ões)"
        return "não determinado"

    def retranslate_ui(self) -> None:
        self.tabs.setTabText(0, tr("Identificação"))
        self.tabs.setTabText(1, tr("Relações"))
        self.tabs.setTabText(2, tr("Clínica"))
        self.edit_button.setText(tr("Editar indivíduo"))
        self.empty.setText(tr("Selecione um indivíduo para consultar ou editar suas propriedades."))
        for widget, text in (
            (self.label_edit, "Identificador exibido"),
            (self.gender_combo, "Símbolo/gênero"),
            (self.phenotype_combo, "Estado fenotípico"),
        ):
            label = self.identity_form.labelForField(widget)
            if label is not None:
                label.setText(tr(text))
        self.deceased_check.setText(tr("Falecido"))
        self.lock_layout_check.setText(tr("Preservar posição no auto-layout"))
        self.apply_button.setText(tr("Aplicar"))
        self.identity_header.setText(tr("Identificação").upper())
        self.relations_header.setText(tr("Relações").upper())
        gender_labels = (
            "Homem/menino",
            "Mulher/menina",
            "Gênero diverso",
            "Não conhecido/especificado",
        )
        for index, text in enumerate(gender_labels):
            self.gender_combo.setItemText(index, tr(text))
        phenotype_labels = ("Desconhecido", "Clinicamente afetado", "Explicitamente não afetado")
        for index, text in enumerate(phenotype_labels):
            self.phenotype_combo.setItemText(index, tr(text))

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
