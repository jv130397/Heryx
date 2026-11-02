"""Clinical HPO editing, family comparison and ontology management surfaces."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.domain import (
    ClinicalCourse,
    ClinicalLaterality,
    ClinicalObservationStatus,
    ClinicalSeverity,
    GenderIdentity,
    HPOObservation,
    KinshipEngine,
    PedigreeProject,
    export_phenotype_matrix_csv,
    phenotype_matrix,
)
from rarepedigree.terminology import (
    HPO_ACKNOWLEDGEMENT,
    HPOIndex,
    HPOTerm,
    install_official_hpo,
)
from rarepedigree.ui.components import AccessibleCheckBox
from rarepedigree.ui.i18n import tr

STATUS_LABELS = {
    ClinicalObservationStatus.PRESENT: "Presente",
    ClinicalObservationStatus.ABSENT: "Ausente",
    ClinicalObservationStatus.UNKNOWN: "Desconhecido",
    ClinicalObservationStatus.NOT_EVALUATED: "Não avaliado",
}


class HPOObservationDialog(QDialog):
    def __init__(
        self,
        term: HPOTerm,
        individual_id: UUID,
        ontology_version: str,
        observation: HPOObservation | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.term = term
        self.individual_id = individual_id
        self.observation = observation
        self.ontology_version = ontology_version
        self.setWindowTitle(tr("Observação HPO"))
        self.setMinimumWidth(520)
        root = QVBoxLayout(self)
        heading = QLabel(f"{term.id} — {term.name}")
        heading.setProperty("sectionHeader", True)
        root.addWidget(heading)
        if term.obsolete:
            warning = QLabel(
                tr("Termo obsoleto")
                + (f" · {tr('Substituído por')} {term.replaced_by}" if term.replaced_by else "")
            )
            warning.setProperty("card", True)
            root.addWidget(warning)
        form = QFormLayout()
        self.status = QComboBox()
        for value, label in STATUS_LABELS.items():
            self.status.addItem(tr(label), value)
        self.onset = QLineEdit()
        self.onset.setPlaceholderText(tr("Ex.: 4 anos, congênito"))
        self.severity = QComboBox()
        for value, label in (
            (ClinicalSeverity.UNKNOWN, "Desconhecida"),
            (ClinicalSeverity.MILD, "Leve"),
            (ClinicalSeverity.MODERATE, "Moderada"),
            (ClinicalSeverity.SEVERE, "Grave"),
        ):
            self.severity.addItem(tr(label), value)
        self.course = QComboBox()
        for value in ClinicalCourse:
            self.course.addItem(tr(value.value.replace("_", " ").title()), value)
        self.laterality = QComboBox()
        for value in ClinicalLaterality:
            self.laterality.addItem(tr(value.value.replace("_", " ").title()), value)
        self.frequency = QLineEdit()
        self.source = QLineEdit()
        self.observed_at = QLineEdit()
        self.observed_at.setPlaceholderText("AAAA-MM-DD")
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(90)
        form.addRow(tr("Estado"), self.status)
        form.addRow(tr("Idade de início"), self.onset)
        form.addRow(tr("Gravidade"), self.severity)
        form.addRow(tr("Evolução"), self.course)
        form.addRow(tr("Lateralidade"), self.laterality)
        form.addRow(tr("Frequência/recorrência"), self.frequency)
        form.addRow(tr("Fonte clínica"), self.source)
        form.addRow(tr("Data da avaliação"), self.observed_at)
        form.addRow(tr("Comentários"), self.notes)
        root.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        if observation:
            self._load(observation)

    def _load(self, item: HPOObservation) -> None:
        self.status.setCurrentIndex(max(0, self.status.findData(item.status)))
        self.onset.setText(item.onset or "")
        self.severity.setCurrentIndex(max(0, self.severity.findData(item.severity)))
        self.course.setCurrentIndex(max(0, self.course.findData(item.course)))
        self.laterality.setCurrentIndex(max(0, self.laterality.findData(item.laterality)))
        self.frequency.setText(item.frequency or "")
        self.source.setText(item.source or "")
        self.observed_at.setText(item.observed_at.date().isoformat() if item.observed_at else "")
        self.notes.setPlainText(item.notes or "")

    def value(self) -> HPOObservation:
        observed_at = None
        if self.observed_at.text().strip():
            observed_at = datetime.fromisoformat(self.observed_at.text().strip())
        values = {
            "individual_id": self.individual_id,
            "hpo_id": self.term.id,
            "term_label": self.term.name,
            "status": self.status.currentData(),
            "observed_at": observed_at,
            "source": self.source.text().strip() or None,
            "notes": self.notes.toPlainText().strip() or None,
            "ontology_version": self.ontology_version,
            "onset": self.onset.text().strip() or None,
            "severity": self.severity.currentData(),
            "frequency": self.frequency.text().strip() or None,
            "course": self.course.currentData(),
            "laterality": self.laterality.currentData(),
        }
        if self.observation:
            return self.observation.model_copy(update=values)
        return HPOObservation(**values)


class HPOClinicalPanel(QWidget):
    """Transactional editor content; changes stay local until the parent Save action."""

    def __init__(self, index: HPOIndex | None = None, parent=None) -> None:
        super().__init__(parent)
        self.index = index or HPOIndex()
        self.individual_id: UUID | None = None
        self.observations: list[HPOObservation] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        self.summary = QLabel()
        self.summary.setProperty("card", True)
        root.addWidget(self.summary)
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("Buscar código, nome ou sinônimo HPO…"))
        self.search.setAccessibleName(tr("Busca HPO"))
        root.addWidget(self.search)
        self.results = QListWidget()
        self.results.setMaximumHeight(140)
        self.results.setVisible(False)
        root.addWidget(self.results)
        self.associated = QListWidget()
        self.associated.setMinimumHeight(150)
        root.addWidget(self.associated, 1)
        actions = QHBoxLayout()
        self.edit_button = QPushButton(tr("Editar observação"))
        self.remove_button = QPushButton(tr("Remover"))
        actions.addWidget(self.edit_button)
        actions.addWidget(self.remove_button)
        actions.addStretch()
        root.addLayout(actions)
        self.status = QLabel()
        root.addWidget(self.status)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(140)
        self.search.textChanged.connect(lambda: self.timer.start())
        self.timer.timeout.connect(self._search)
        self.results.itemActivated.connect(self._add_result)
        self.results.itemClicked.connect(self._add_result)
        self.associated.itemDoubleClicked.connect(lambda _item: self._edit())
        self.edit_button.clicked.connect(self._edit)
        self.remove_button.clicked.connect(self._remove)

    def set_data(self, individual_id: UUID, observations: list[HPOObservation]) -> None:
        self.individual_id = individual_id
        self.observations = [item.model_copy(deep=True) for item in observations]
        self.search.clear()
        self.results.hide()
        self._refresh()

    def _search(self) -> None:
        self.results.clear()
        query = self.search.text().strip()
        if not query:
            self.results.hide()
            return
        if not self.index.installed:
            self.status.setText(tr("HPO não instalada. Use Preferências para instalar."))
            self.results.hide()
            return
        for term in self.index.search(query, 20):
            suffix = f" · {tr('obsoleto')}" if term.obsolete else ""
            item = QListWidgetItem(f"{term.id} — {term.name}{suffix}")
            item.setData(256, term)
            item.setToolTip(term.definition)
            self.results.addItem(item)
        self.results.setVisible(self.results.count() > 0)
        self.status.setText(
            tr("Nenhum termo encontrado") if self.results.count() == 0 else ""
        )

    def _add_result(self, item: QListWidgetItem) -> None:
        if self.individual_id is None:
            return
        term = item.data(256)
        metadata = self.index.metadata()
        dialog = HPOObservationDialog(
            term,
            self.individual_id,
            metadata.version if metadata else "unknown",
            parent=self,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        value = dialog.value()
        if any(
            current.hpo_id == value.hpo_id and current.observed_at == value.observed_at
            for current in self.observations
        ):
            QMessageBox.warning(self, tr("Registro duplicado"), tr("Este termo e data já existem."))
            return
        self.observations.append(value)
        self.search.clear()
        self._refresh()

    def _edit(self) -> None:
        row = self.associated.currentRow()
        if row < 0:
            return
        current = self.observations[row]
        term = self.index.term(current.hpo_id) or HPOTerm(current.hpo_id, current.term_label)
        dialog = HPOObservationDialog(
            term, current.individual_id, current.ontology_version, current, self
        )
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.observations[row] = dialog.value()
            self._refresh()

    def _remove(self) -> None:
        row = self.associated.currentRow()
        if row >= 0:
            self.observations.pop(row)
            self._refresh()

    def _refresh(self) -> None:
        self.associated.clear()
        for observation in self.observations:
            label = tr(STATUS_LABELS[observation.status])
            detail = f"{observation.hpo_id} — {observation.term_label}\n{label}"
            if observation.onset:
                detail += f" · {tr('Início')}: {observation.onset}"
            item = QListWidgetItem(detail)
            item.setToolTip(observation.notes or observation.source or "")
            self.associated.addItem(item)
        present = sum(
            item.status == ClinicalObservationStatus.PRESENT for item in self.observations
        )
        absent = sum(item.status == ClinicalObservationStatus.ABSENT for item in self.observations)
        self.summary.setText(
            f"{len(self.observations)} {tr('fenótipos')} · "
            f"{present} {tr('presentes')} · {absent} {tr('ausentes')}"
        )


class HPOInstallWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def run(self) -> None:
        try:
            self.succeeded.emit(install_official_hpo())
        except Exception as error:  # pragma: no cover - network/system dependent
            self.failed.emit(str(error))


class HPOManagerDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Ontologia HPO"))
        self.setMinimumWidth(560)
        self.index = HPOIndex()
        root = QVBoxLayout(self)
        self.metadata = QLabel()
        self.metadata.setWordWrap(True)
        self.metadata.setProperty("card", True)
        root.addWidget(self.metadata)
        acknowledgement = QLabel(HPO_ACKNOWLEDGEMENT + " https://hpo.jax.org/")
        acknowledgement.setWordWrap(True)
        root.addWidget(acknowledgement)
        self.install = QPushButton(tr("Instalar/atualizar HPO oficial"))
        self.install.clicked.connect(self._start)
        root.addWidget(self.install)
        self.progress = QLabel()
        root.addWidget(self.progress)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject)
        root.addWidget(close)
        self.worker: HPOInstallWorker | None = None
        self._refresh()

    def _refresh(self) -> None:
        metadata = self.index.metadata()
        self.metadata.setText(
            (
                f"{tr('Versão instalada')}: {metadata.version}\n"
                f"{tr('Termos')}: {metadata.term_count}\n"
                f"SHA-256: {metadata.sha256}\n{tr('Fonte')}: {metadata.source}"
            )
            if metadata
            else tr("Nenhuma versão HPO instalada. O editor continua disponível offline.")
        )

    def _start(self) -> None:
        self.install.setEnabled(False)
        self.progress.setText(tr("Baixando e validando fora da interface…"))
        self.worker = HPOInstallWorker(self)
        self.worker.succeeded.connect(self._installed)
        self.worker.failed.connect(self._failed)
        self.worker.start()

    def _installed(self, _release) -> None:
        self.install.setEnabled(True)
        self.progress.setText(tr("HPO instalada com sucesso"))
        self._refresh()

    def _failed(self, message: str) -> None:
        self.install.setEnabled(True)
        self.progress.setText(tr("Falha na atualização; a base anterior foi preservada."))
        QMessageBox.warning(self, tr("Falha na atualização HPO"), message)


class FamilyPhenotypeComparisonDialog(QDialog):
    highlightRequested = Signal(str)

    def __init__(self, project: PedigreeProject, parent=None) -> None:
        super().__init__(parent)
        self.project = project
        self.setWindowTitle(tr("Comparação fenotípica familiar"))
        self.resize(900, 560)
        root = QVBoxLayout(self)
        root.addWidget(QLabel(tr("Selecione os indivíduos e compare observações documentadas.")))
        filters = QHBoxLayout()
        self.generation = QComboBox()
        self.generation.addItem(tr("Todas as gerações"), None)
        levels = sorted({round(person.layout.y) for person in project.individuals})
        for index, level in enumerate(levels, 1):
            self.generation.addItem(f"{tr('Geração')} {index}", level)
        self.branch = QComboBox()
        self.branch.addItem(tr("Todos os ramos"), "all")
        self.branch.addItem(tr("Ramo materno"), "maternal")
        self.branch.addItem(tr("Ramo paterno"), "paternal")
        filters.addWidget(self.generation)
        filters.addWidget(self.branch)
        root.addLayout(filters)
        self.people = QListWidget()
        self.people.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for person in project.individuals:
            item = QListWidgetItem(person.label)
            item.setData(256, person.id)
            item.setSelected(True)
            self.people.addItem(item)
        self.people.setMaximumHeight(120)
        root.addWidget(self.people)
        self.generation.currentIndexChanged.connect(self._apply_filters)
        self.branch.currentIndexChanged.connect(self._apply_filters)
        self.table = QTableWidget()
        root.addWidget(self.table, 1)
        actions = QHBoxLayout()
        refresh = QPushButton(tr("Atualizar matriz"))
        export = QPushButton(tr("Exportar CSV…"))
        self.deidentify = AccessibleCheckBox(tr("Desidentificar identificadores"))
        refresh.clicked.connect(self.refresh)
        export.clicked.connect(self._export)
        actions.addWidget(refresh)
        actions.addWidget(export)
        actions.addWidget(self.deidentify)
        actions.addStretch()
        root.addLayout(actions)
        self.table.cellClicked.connect(self._highlight)
        self.refresh()

    def selected_ids(self) -> list[UUID]:
        return [item.data(256) for item in self.people.selectedItems()]

    def _apply_filters(self) -> None:
        generation = self.generation.currentData()
        branch = self.branch.currentData()
        allowed = {person.id for person in self.project.individuals}
        if generation is not None:
            allowed &= {
                person.id
                for person in self.project.individuals
                if round(person.layout.y) == generation
            }
        if branch != "all":
            proband = next((person for person in self.project.individuals if person.proband), None)
            if proband:
                engine = KinshipEngine()
                parents = engine.parents(self.project, proband.id)
                gender = GenderIdentity.WOMAN if branch == "maternal" else GenderIdentity.MAN
                people = {person.id: person for person in self.project.individuals}
                root = next(
                    (
                        parent_id
                        for parent_id in parents
                        if people[parent_id].gender_identity == gender
                    ),
                    None,
                )
                branch_ids = {root} if root else set()
                if root:
                    branch_ids |= set(engine.ancestors(self.project, root))
                allowed &= branch_ids
        for row in range(self.people.count()):
            item = self.people.item(row)
            item.setHidden(item.data(256) not in allowed)
            item.setSelected(item.data(256) in allowed)
        self.refresh()

    def refresh(self) -> None:
        selected = self.selected_ids()
        people = {person.id: person for person in self.project.individuals}
        _, rows = phenotype_matrix(self.project, selected)
        self.table.setColumnCount(2 + len(selected))
        self.table.setHorizontalHeaderLabels(
            [tr("Código HPO"), tr("Fenótipo"), *(people[item].label for item in selected)]
        )
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                text = (
                    tr(STATUS_LABELS.get(ClinicalObservationStatus(value), value))
                    if column_index >= 2
                    else value
                )
                self.table.setItem(row_index, column_index, QTableWidgetItem(text))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def _highlight(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item:
            self.highlightRequested.emit(item.text())

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, tr("Exportar matriz"), "", "CSV (*.csv)")
        if path:
            export_phenotype_matrix_csv(
                self.project,
                self.selected_ids(),
                Path(path),
                deidentify=self.deidentify.isChecked(),
            )
