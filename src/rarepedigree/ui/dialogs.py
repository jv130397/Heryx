"""Focused editing and project creation dialogs."""

from pathlib import Path
from typing import Any
from uuid import UUID

from PySide6.QtCore import QPointF, QRectF, QSettings, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    KinshipEngine,
    KinshipPlan,
    ObservationStatus,
    PedigreeProject,
    SiblingKind,
)
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.rendering import PedigreeScene
from rarepedigree.ui.components import NexusDialogHeader
from rarepedigree.ui.i18n import language_manager, tr


class ImportProjectDialog(QDialog):
    """Proportional import surface; parsing remains in the repository layer."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Importar projeto"))
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        layout.addWidget(
            NexusDialogHeader(
                tr("Importar projeto"),
                tr("Abra um projeto RarePedigree compatível"),
            )
        )
        form = QFormLayout()
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(tr("Selecione um arquivo .rps.json"))
        browse = QPushButton(tr("Procurar…"))
        browse.clicked.connect(self._browse)
        row_layout.addWidget(self.path_edit, 1)
        row_layout.addWidget(browse)
        form.addRow(tr("Arquivo"), row)
        self.note = QLabel(
            tr("O conteúdo será validado antes de substituir o projeto aberto.")
        )
        self.note.setWordWrap(True)
        self.note.setProperty("card", True)
        form.addRow(self.note)
        layout.addLayout(form)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.StandardButton.Open).setText(tr("Importar"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))
        layout.addWidget(self.buttons)

    def _browse(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, tr("Importar projeto"), "", "RarePedigree (*.rps.json *.json)"
        )
        if filename:
            self.path_edit.setText(filename)

    def selected_path(self) -> Path | None:
        value = self.path_edit.text().strip()
        return Path(value) if value else None

    def accept(self) -> None:
        if self.selected_path() is None:
            QMessageBox.warning(self, tr("Arquivo necessário"), tr("Selecione um projeto."))
            return
        super().accept()


class ExportFigureDialog(QDialog):
    """Presentation and export options without claiming unsupported formats."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Exportar heredograma"))
        self.setMinimumWidth(660)
        settings = language_manager.settings
        layout = QVBoxLayout(self)
        layout.addWidget(
            NexusDialogHeader(
                tr("Exportar heredograma"),
                tr("Escolha o formato e a apresentação da figura"),
            )
        )
        form = QFormLayout()
        self.format = QComboBox()
        self.format.addItem("SVG — " + tr("vetorial"), "svg")
        self.format.addItem("PNG — " + tr("imagem"), "png")
        self.format.addItem("PDF — " + tr("documento"), "pdf")
        self.path_edit = QLineEdit("heredograma.svg")
        self.format.currentIndexChanged.connect(self._sync_suffix)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        browse = QPushButton(tr("Procurar…"))
        browse.clicked.connect(self._browse)
        row_layout.addWidget(self.path_edit, 1)
        row_layout.addWidget(browse)
        self.include_legend = QCheckBox(tr("Incluir legenda científica"))
        self.include_legend.setChecked(settings.value("export/include_legend", True, bool))
        self.monochrome = QCheckBox(tr("Modo científico monocromático"))
        self.monochrome.setChecked(settings.value("export/monochrome", False, bool))
        form.addRow(tr("Formato"), self.format)
        form.addRow(tr("Destino"), row)
        form.addRow(self.include_legend)
        form.addRow(self.monochrome)
        layout.addLayout(form)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("Exportar"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))
        layout.addWidget(self.buttons)

    def _sync_suffix(self) -> None:
        path = Path(self.path_edit.text())
        self.path_edit.setText(str(path.with_suffix("." + self.format.currentData())))

    def _browse(self) -> None:
        extension = self.format.currentData()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            tr("Exportar heredograma"),
            self.path_edit.text(),
            f"{extension.upper()} (*.{extension})",
        )
        if filename:
            self.path_edit.setText(filename)

    def selected_path(self) -> Path | None:
        value = self.path_edit.text().strip()
        return Path(value).with_suffix("." + self.format.currentData()) if value else None


class LabelConfigurationDialog(QDialog):
    """Presentation-only label configuration; never rewrites individuals."""

    applied = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.settings = QSettings()
        self.setWindowTitle(tr("Configurar rótulos"))
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        layout.addWidget(
            NexusDialogHeader(
                tr("Configurar rótulos"),
                tr("Escolha como identificar os indivíduos no canvas"),
            )
        )
        form = QFormLayout()
        self.mode = QComboBox()
        self.mode.addItem(tr("Identificador manual"), "manual")
        self.mode.addItem(tr("Numeração genealógica (I-1, II-3)"), "genealogical")
        self.mode.addItem(tr("Numeração e identificador manual"), "both")
        self.mode.setCurrentIndex(
            max(
                0,
                self.mode.findData(
                    self.settings.value("pedigree/identifier_mode", "manual", str)
                ),
            )
        )
        self.auxiliary = QCheckBox(tr("Mostrar rótulos auxiliares"))
        self.auxiliary.setChecked(
            self.settings.value("pedigree/show_auxiliary_labels", True, bool)
        )
        self.preview = QLabel()
        self.preview.setProperty("card", True)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addRow(tr("Rótulo principal"), self.mode)
        form.addRow(self.auxiliary)
        form.addRow(tr("Prévia"), self.preview)
        layout.addLayout(form)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("Aplicar"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))
        buttons.accepted.connect(self._apply)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.mode.currentIndexChanged.connect(self._update_preview)
        self._update_preview()

    def _update_preview(self) -> None:
        examples = {
            "manual": "João",
            "genealogical": "III-2",
            "both": "III-2 · João",
        }
        self.preview.setText(examples[self.mode.currentData()])

    def _apply(self) -> None:
        self.settings.setValue("pedigree/identifier_mode", self.mode.currentData())
        self.settings.setValue("pedigree/show_auxiliary_labels", self.auxiliary.isChecked())
        self.settings.sync()
        self.applied.emit()
        self.accept()


class SymbolPreview(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.gender = GenderIdentity.UNKNOWN
        self.status = ObservationStatus.UNKNOWN
        self.deceased = False
        self.setMinimumSize(150, 120)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.width() / 2 - 28, 26, 56, 56)
        painter.setPen(QPen(QColor("#078FC2"), 4))
        painter.setBrush(
            QColor("#1C293B") if self.status == ObservationStatus.PRESENT else QColor("white")
        )
        if self.gender == GenderIdentity.MAN:
            painter.drawRect(rect)
        elif self.gender == GenderIdentity.WOMAN:
            painter.drawEllipse(rect)
        else:
            center = rect.center()
            painter.drawPolygon(
                [
                    center + QPointF(0, -28),
                    center + QPointF(28, 0),
                    center + QPointF(0, 28),
                    center + QPointF(-28, 0),
                ]
            )
        if self.status == ObservationStatus.UNKNOWN:
            painter.setPen(QColor("#334155"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "?")
        if self.deceased:
            painter.drawLine(rect.bottomLeft(), rect.topRight())


class EditIndividualDialog(QDialog):
    def __init__(self, person: Individual, parent=None) -> None:
        super().__init__(parent)
        self.person = person
        self.setWindowTitle(tr("Editar indivíduo"))
        self.setMinimumWidth(560)
        root = QVBoxLayout(self)
        root.addWidget(
            NexusDialogHeader(
                tr("Editar indivíduo"),
                tr("Identificação e representação científica"),
            )
        )
        body = QWidget()
        body_layout = QHBoxLayout(body)
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        self.form = form
        self.label_edit = QLineEdit(person.label)
        self.symbol_group = QButtonGroup(self)
        symbol_row = QWidget()
        symbol_layout = QHBoxLayout(symbol_row)
        for label, value in (
            ("□", GenderIdentity.MAN),
            ("○", GenderIdentity.WOMAN),
            ("◇", GenderIdentity.UNKNOWN),
        ):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setProperty("symbolCard", True)
            self.symbol_group.addButton(button)
            button.setProperty("value", value)
            symbol_layout.addWidget(button)
            if value == person.gender_identity:
                button.setChecked(True)
        self.phenotype = QComboBox()
        self.phenotype.addItem("Desconhecido", ObservationStatus.UNKNOWN)
        self.phenotype.addItem("Afetado", ObservationStatus.PRESENT)
        self.phenotype.addItem("Não afetado", ObservationStatus.ABSENT)
        self.phenotype.setCurrentIndex(self.phenotype.findData(person.phenotype_status))
        self.deceased = QCheckBox("Falecido")
        self.deceased.setChecked(person.deceased)
        self.proband = QCheckBox("Proband")
        self.proband.setChecked(person.proband)
        self.consultand = QCheckBox("Consultand")
        self.consultand.setChecked(person.consultand)
        form.addRow("Identificador", self.label_edit)
        form.addRow("Símbolo", symbol_row)
        form.addRow("Estado fenotípico", self.phenotype)
        form.addRow(self.deceased)
        form.addRow(self.proband)
        form.addRow(self.consultand)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        form.addRow(self.buttons)
        self.preview = SymbolPreview()
        body_layout.addWidget(form_widget, 2)
        body_layout.addWidget(self.preview, 1)
        root.addWidget(body)
        self.symbol_group.buttonClicked.connect(self._update_preview)
        self.phenotype.currentIndexChanged.connect(self._update_preview)
        self.deceased.toggled.connect(self._update_preview)
        self._update_preview()
        language_manager.languageChanged.connect(self.retranslate_ui)
        self.retranslate_ui()

    def retranslate_ui(self, _language=None) -> None:
        self.setWindowTitle(tr("Editar indivíduo"))
        for widget, text in (
            (self.label_edit, "Identificador exibido"),
            (self.phenotype, "Estado fenotípico"),
        ):
            label = self.form.labelForField(widget)
            if label is not None:
                label.setText(tr(text))
        self.deceased.setText(tr("Falecido"))
        for index, text in enumerate(("Desconhecido", "Afetado", "Não afetado")):
            self.phenotype.setItemText(index, tr(text))
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("Salvar"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))

    def _update_preview(self) -> None:
        checked = self.symbol_group.checkedButton()
        self.preview.gender = checked.property("value") if checked else GenderIdentity.UNKNOWN
        self.preview.status = self.phenotype.currentData()
        self.preview.deceased = self.deceased.isChecked()
        self.preview.update()

    def values(self) -> dict[str, Any]:
        checked = self.symbol_group.checkedButton()
        return {
            "label": self.label_edit.text().strip() or "Indivíduo",
            "gender_identity": checked.property("value") if checked else GenderIdentity.UNKNOWN,
            "phenotype_status": self.phenotype.currentData(),
            "deceased": self.deceased.isChecked(),
            "proband": self.proband.isChecked(),
            "consultand": self.consultand.isChecked(),
        }


class AddSiblingDialog(QDialog):
    """Small first-step assistant that makes shared parentage explicit."""

    def __init__(self, reference: Individual, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Adicionar irmão ou irmã"))
        self.setMinimumWidth(540)
        self.form = QFormLayout(self)
        self.form.addRow(
            NexusDialogHeader(
                tr("Adicionar irmão ou irmã"),
                tr("Defina explicitamente o núcleo parental compartilhado"),
            )
        )
        self.name = QLineEdit()
        self.name.setPlaceholderText(tr("Identificador exibido"))
        self.kind = QComboBox()
        for text, value in (
            ("Mesmo pai e mesma mãe", SiblingKind.FULL),
            ("Somente o pai", SiblingKind.PATERNAL_HALF),
            ("Somente a mãe", SiblingKind.MATERNAL_HALF),
            ("Parentalidade ainda não esclarecida", SiblingKind.UNRESOLVED),
            ("Vínculo adotivo", SiblingKind.ADOPTIVE),
            ("Vínculo social", SiblingKind.SOCIAL),
        ):
            self.kind.addItem(tr(text), value)
        self.preview = QLabel()
        self.preview.setWordWrap(True)
        self.preview.setProperty("card", True)
        self.form.addRow(tr("Pessoa de referência"), QLabel(reference.label))
        self.form.addRow(tr("Identificador"), self.name)
        self.form.addRow(tr("Vínculo parental"), self.kind)
        self.form.addRow(tr("Prévia"), self.preview)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form.addRow(self.buttons)
        self.kind.currentIndexChanged.connect(self._update_preview)
        self._update_preview()

    def _update_preview(self) -> None:
        messages = {
            SiblingKind.FULL: "Os dois genitores biológicos serão reutilizados.",
            SiblingKind.PATERNAL_HALF: "O pai será compartilhado; a mãe será diferente.",
            SiblingKind.MATERNAL_HALF: "A mãe será compartilhada; o pai será diferente.",
            SiblingKind.UNRESOLVED: "Nenhum genitor será presumido.",
            SiblingKind.ADOPTIVE: "O vínculo não será usado como ancestralidade genética.",
            SiblingKind.SOCIAL: "O vínculo não será usado como ancestralidade genética.",
        }
        self.preview.setText(tr(messages[self.sibling_kind()]))

    def sibling_kind(self) -> SiblingKind:
        return SiblingKind(self.kind.currentData())

    def sibling_label(self) -> str | None:
        return self.name.text().strip() or None


class AddRelativeWizard(QWizard):
    """Five-step, non-mutating assistant backed exclusively by KinshipEngine."""

    def __init__(self, project: PedigreeProject, reference: Individual, parent=None) -> None:
        super().__init__(parent)
        self.project = project.model_copy(deep=True)
        self.reference = reference
        self.engine = KinshipEngine()
        self._plan: KinshipPlan | None = None
        self.setWindowTitle(tr("Adicionar familiar"))
        self.setMinimumSize(860, 620)
        self._create_pages()
        self.currentIdChanged.connect(self._page_changed)

    def _create_pages(self) -> None:
        identity = QWizardPage()
        identity.setTitle(tr("1. Identificação"))
        identity_form = QFormLayout(identity)
        self.relative_label = QLineEdit("Novo familiar")
        self.relative_gender = QComboBox()
        self.relative_gender.addItem(tr("Não especificado"), GenderIdentity.UNKNOWN)
        self.relative_gender.addItem(tr("Homem/menino"), GenderIdentity.MAN)
        self.relative_gender.addItem(tr("Mulher/menina"), GenderIdentity.WOMAN)
        identity_form.addRow(tr("Identificador"), self.relative_label)
        identity_form.addRow(tr("Representação"), self.relative_gender)
        self.addPage(identity)

        relation = QWizardPage()
        relation.setTitle(tr("2. Parentesco"))
        relation_form = QFormLayout(relation)
        self.relative_kind = QComboBox()
        entries = (
            ("Pai", "father"),
            ("Mãe", "mother"),
            ("Genitor não especificado", "parent_unspecified"),
            ("Avô paterno", "paternal_grandfather"),
            ("Avó paterna", "paternal_grandmother"),
            ("Avô materno", "maternal_grandfather"),
            ("Avó materna", "maternal_grandmother"),
            ("Bisavô pelo ramo paterno", "paternal_great_grandfather"),
            ("Filho/filha", "child"),
            ("Neto/neta", "grandchild"),
            ("Bisneto/bisneta", "great_grandchild"),
            ("Irmão completo", "full_sibling"),
            ("Meio-irmão paterno", "paternal_half_sibling"),
            ("Meio-irmão materno", "maternal_half_sibling"),
            ("Irmão com parentalidade não esclarecida", "unresolved_sibling"),
            ("Irmão adotivo", "adoptive_sibling"),
            ("Irmão social", "social_sibling"),
            ("Tio/tia paterno", "paternal_aunt_uncle"),
            ("Tio/tia materno", "maternal_aunt_uncle"),
            ("Primo/prima paterno", "paternal_cousin"),
            ("Primo/prima materno", "maternal_cousin"),
            ("Sobrinho/sobrinha", "nephew_niece"),
        )
        for text, value in entries:
            self.relative_kind.addItem(tr(text), value)
        relation_form.addRow(tr("Relação com o indivíduo selecionado"), self.relative_kind)
        self.addPage(relation)

        resolution = QWizardPage()
        resolution.setTitle(tr("3. Genitores e intermediários"))
        resolution_form = QFormLayout(resolution)
        self.allow_intermediates = QCheckBox(
            tr("Autorizar representantes desconhecidos quando o caminho exigir")
        )
        self.allow_intermediates.setChecked(True)
        self.existing_other_parent = QComboBox()
        self.existing_other_parent.addItem(tr("Manter outro genitor desconhecido"), None)
        for person in self.project.individuals:
            if person.id != self.reference.id:
                self.existing_other_parent.addItem(person.label, str(person.id))
        self.resolution_help = QLabel(
            tr(
                "O motor reutilizará familiares compatíveis. Nenhum casamento será inferido "
                "a partir de coparentalidade."
            )
        )
        self.resolution_help.setWordWrap(True)
        resolution_form.addRow(self.allow_intermediates)
        resolution_form.addRow(tr("Outro genitor existente"), self.existing_other_parent)
        resolution_form.addRow(self.resolution_help)
        self.addPage(resolution)

        preview = QWizardPage()
        preview.setTitle(tr("4. Prévia estrutural"))
        preview_layout = QVBoxLayout(preview)
        self.preview_view = QGraphicsView()
        self.preview_view.setMinimumHeight(360)
        self.preview_summary = QLabel()
        self.preview_summary.setWordWrap(True)
        preview_layout.addWidget(self.preview_view)
        preview_layout.addWidget(self.preview_summary)
        self.addPage(preview)

        confirmation = QWizardPage()
        confirmation.setTitle(tr("5. Confirmação"))
        confirmation_layout = QVBoxLayout(confirmation)
        self.confirmation_text = QLabel()
        self.confirmation_text.setWordWrap(True)
        confirmation_layout.addWidget(self.confirmation_text)
        confirmation_layout.addStretch()
        self.addPage(confirmation)

    def _page_changed(self, page_id: int) -> None:
        if page_id not in {3, 4}:
            return
        try:
            self._plan = self.build_plan()
        except ValueError as error:
            self._plan = None
            self.preview_summary.setText(tr(str(error)))
            return
        if page_id == 3:
            preview_project = self._plan.after.model_copy(deep=True)
            positions = PedigreeLayoutEngine().compute(preview_project, preserve_locked=False)
            for person in preview_project.individuals:
                person.layout.x, person.layout.y = positions[person.id]
            scene = PedigreeScene()
            scene.load_project(preview_project)
            self.preview_view.setScene(scene)
            self.preview_view.fitInView(
                scene.pedigree_bounding_rect().adjusted(-70, -50, 70, 70),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            self.preview_summary.setText(self._summary(self._plan))
        else:
            self.confirmation_text.setText(
                tr("A operação será aplicada como uma única ação reversível.\n\n")
                + self._summary(self._plan)
            )

    def build_plan(self) -> KinshipPlan:
        kind = self.relative_kind.currentData()
        label = self.relative_label.text().strip() or "Novo familiar"
        gender = GenderIdentity(self.relative_gender.currentData())
        allow = self.allow_intermediates.isChecked()
        reference_id = self.reference.id
        other_parent_data = self.existing_other_parent.currentData()
        other_parent_id = UUID(other_parent_data) if other_parent_data else None
        ancestor_paths = {
            "father": [GenderIdentity.MAN],
            "mother": [GenderIdentity.WOMAN],
            "parent_unspecified": [GenderIdentity.UNKNOWN],
            "paternal_grandfather": [GenderIdentity.MAN, GenderIdentity.MAN],
            "paternal_grandmother": [GenderIdentity.MAN, GenderIdentity.WOMAN],
            "maternal_grandfather": [GenderIdentity.WOMAN, GenderIdentity.MAN],
            "maternal_grandmother": [GenderIdentity.WOMAN, GenderIdentity.WOMAN],
            "paternal_great_grandfather": [
                GenderIdentity.MAN,
                GenderIdentity.MAN,
                GenderIdentity.MAN,
            ],
        }
        if kind in ancestor_paths:
            return self.engine.plan_ancestor_path(
                self.project,
                reference_id,
                ancestor_paths[kind],
                label=label,
                create_missing_intermediates=allow,
            )
        if kind in {"child", "grandchild", "great_grandchild"}:
            if kind == "child":
                plan = self.engine.plan_child(
                    self.project,
                    reference_id,
                    coparent_id=other_parent_id,
                    label=label,
                )
                self.engine._person(plan.after, plan.created_ids[0]).gender_identity = gender
                plan.after = PedigreeProject.model_validate(plan.after.model_dump())
                return plan
            return self.engine.plan_descendant(
                self.project,
                reference_id,
                {"child": 1, "grandchild": 2, "great_grandchild": 3}[kind],
                label=label,
                gender=gender,
                create_missing_intermediates=allow,
            )
        sibling_kinds = {
            "full_sibling": SiblingKind.FULL,
            "paternal_half_sibling": SiblingKind.PATERNAL_HALF,
            "maternal_half_sibling": SiblingKind.MATERNAL_HALF,
            "unresolved_sibling": SiblingKind.UNRESOLVED,
            "adoptive_sibling": SiblingKind.ADOPTIVE,
            "social_sibling": SiblingKind.SOCIAL,
        }
        if kind in sibling_kinds:
            plan = self.engine.plan_sibling(
                self.project,
                reference_id,
                sibling_kinds[kind],
                label=label,
                other_parent_id=other_parent_id,
                create_missing_parents=allow,
            )
            self.engine._person(plan.after, plan.created_ids[0]).gender_identity = gender
            return plan
        if kind in {"paternal_aunt_uncle", "maternal_aunt_uncle"}:
            return self.engine.plan_aunt_uncle(
                self.project,
                reference_id,
                branch_gender=(
                    GenderIdentity.MAN if kind.startswith("paternal") else GenderIdentity.WOMAN
                ),
                relative_gender=gender,
                label=label,
                create_missing_intermediates=allow,
            )
        if kind in {"paternal_cousin", "maternal_cousin"}:
            return self.engine.plan_cousin(
                self.project,
                reference_id,
                branch_gender=(
                    GenderIdentity.MAN if kind.startswith("paternal") else GenderIdentity.WOMAN
                ),
                cousin_gender=gender,
                label=label,
                create_missing_intermediates=allow,
            )
        if kind == "nephew_niece":
            return self.engine.plan_nephew_niece(self.project, reference_id, label=label)
        raise ValueError("parentesco ainda não suportado")

    def result_plan(self) -> KinshipPlan:
        if self._plan is None:
            self._plan = self.build_plan()
        return self._plan

    @staticmethod
    def _summary(plan: KinshipPlan) -> str:
        return tr(
            f"Novos indivíduos: {len(plan.created_ids)} | "
            f"Reutilizados: {len(set(plan.reused_ids))} | "
            f"Desconhecidos: {len(set(plan.unknown_ids))}\n"
        ) + "\n".join(plan.notes)

    def accept(self) -> None:
        try:
            self._plan = self.build_plan()
        except ValueError as error:
            QMessageBox.warning(self, tr("Relação inválida"), tr(str(error)))
            return
        super().accept()


class EditSiblingRelationshipDialog(QDialog):
    """Preview a reversible sibling-kind replacement for two existing people."""

    def __init__(
        self,
        project: PedigreeProject,
        first: Individual,
        second: Individual,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.project = project.model_copy(deep=True)
        self.first = first
        self.second = second
        self.engine = KinshipEngine()
        self._plan: KinshipPlan | None = None
        self.setWindowTitle(tr("Editar parentesco entre irmãos"))
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        layout.addWidget(
            NexusDialogHeader(
                tr("Editar parentesco entre irmãos"),
                tr("Revise o impacto antes de confirmar a alteração"),
            )
        )
        self.description = QLabel(tr(f"Alterar o vínculo entre {first.label} e {second.label}."))
        self.kind = QComboBox()
        for text, value in (
            ("Mesmo pai e mesma mãe", SiblingKind.FULL),
            ("Somente o pai", SiblingKind.PATERNAL_HALF),
            ("Somente a mãe", SiblingKind.MATERNAL_HALF),
            ("Parentalidade ainda não esclarecida", SiblingKind.UNRESOLVED),
            ("Vínculo adotivo", SiblingKind.ADOPTIVE),
            ("Vínculo social", SiblingKind.SOCIAL),
        ):
            self.kind.addItem(tr(text), value.value)
        self.impact = QLabel()
        self.impact.setWordWrap(True)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.kind.currentIndexChanged.connect(self._refresh)
        layout.addWidget(self.description)
        layout.addWidget(self.kind)
        layout.addWidget(self.impact)
        layout.addWidget(self.buttons)
        self._refresh()

    def _refresh(self) -> None:
        try:
            self._plan = self.engine.plan_change_sibling_kind(
                self.project,
                self.first.id,
                self.second.id,
                SiblingKind(self.kind.currentData()),
            )
            self.impact.setText("\n".join(self._plan.notes))
        except ValueError as error:
            self._plan = None
            self.impact.setText(tr(str(error)))

    def result_plan(self) -> KinshipPlan:
        if self._plan is None:
            raise ValueError(self.impact.text())
        return self._plan

    def accept(self) -> None:
        self._refresh()
        if self._plan is None:
            QMessageBox.warning(self, tr("Relação inválida"), self.impact.text())
            return
        super().accept()


class ReassignBranchWizard(QWizard):
    """Preview and atomically migrate a collateral relative between branches."""

    def __init__(
        self,
        project: PedigreeProject,
        proband: Individual,
        relative: Individual,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.project = project.model_copy(deep=True)
        self.proband = proband
        self.relative = relative
        self.engine = KinshipEngine()
        self._plan: KinshipPlan | None = None
        self.setWindowTitle(tr("Corrigir ramo familiar"))
        self.resize(880, 640)

        current_page = QWizardPage()
        current_page.setTitle(tr("1. Parentesco atual"))
        self.current_summary = QLabel()
        self.current_summary.setWordWrap(True)
        current_layout = QVBoxLayout(current_page)
        current_layout.addWidget(self.current_summary)
        current_layout.addStretch()
        self.addPage(current_page)

        target_page = QWizardPage()
        target_page.setTitle(tr("2. Ramo correto"))
        target_form = QFormLayout(target_page)
        self.target_branch = QComboBox()
        self.target_branch.addItem(tr("Ramo paterno"), GenderIdentity.MAN.value)
        self.target_branch.addItem(tr("Ramo materno"), GenderIdentity.WOMAN.value)
        self.sibling_kind = QComboBox()
        self.sibling_kind.addItem(tr("Irmão completo do genitor"), SiblingKind.FULL.value)
        self.sibling_kind.addItem(
            tr("Meio-irmão paterno do genitor"), SiblingKind.PATERNAL_HALF.value
        )
        self.sibling_kind.addItem(
            tr("Meio-irmão materno do genitor"), SiblingKind.MATERNAL_HALF.value
        )
        self.create_missing = QCheckBox(tr("Autorizar criação do genitor de destino ausente"))
        target_form.addRow(tr("Novo ramo"), self.target_branch)
        target_form.addRow(tr("Vínculo do intermediário"), self.sibling_kind)
        target_form.addRow(self.create_missing)
        self.addPage(target_page)

        impact_page = QWizardPage()
        impact_page.setTitle(tr("3. Impacto e prévia"))
        impact_layout = QVBoxLayout(impact_page)
        self.impact = QLabel()
        self.impact.setWordWrap(True)
        self.preview = QGraphicsView()
        self.preview.setMinimumHeight(360)
        impact_layout.addWidget(self.impact)
        impact_layout.addWidget(self.preview)
        self.addPage(impact_page)

        confirm_page = QWizardPage()
        confirm_page.setTitle(tr("4. Confirmação"))
        self.confirmation = QLabel()
        self.confirmation.setWordWrap(True)
        confirm_layout = QVBoxLayout(confirm_page)
        confirm_layout.addWidget(self.confirmation)
        confirm_layout.addStretch()
        self.addPage(confirm_page)
        self.currentIdChanged.connect(self._refresh)
        self.target_branch.currentIndexChanged.connect(self._refresh)
        self.sibling_kind.currentIndexChanged.connect(self._refresh)
        self.create_missing.toggled.connect(self._refresh)
        self._refresh()

    def _refresh(self, *_args) -> None:
        context = self.engine.collateral_context(
            self.project, self.proband.id, self.relative.id
        )
        if context is None:
            self.current_summary.setText(tr("O parentesco colateral não pôde ser determinado."))
            self._plan = None
            return
        kind, branch_id, intermediary_id = context
        people = {person.id: person for person in self.project.individuals}
        self.current_summary.setText(
            tr("Familiar")
            + f": {self.relative.label}\n"
            + tr("Tipo")
            + f": {kind}\n"
            + tr("Ramo atual")
            + f": {people[branch_id].label}\n"
            + tr("Intermediário")
            + f": {people[intermediary_id].label}"
        )
        try:
            self._plan = self.engine.plan_reassign_collateral_branch(
                self.project,
                self.proband.id,
                self.relative.id,
                GenderIdentity(self.target_branch.currentData()),
                sibling_kind=SiblingKind(self.sibling_kind.currentData()),
                create_missing_branch=self.create_missing.isChecked(),
            )
        except ValueError as error:
            self._plan = None
            self.impact.setText(tr(str(error)))
            self.confirmation.setText(tr(str(error)))
            return
        self.impact.setText("\n".join(self._plan.notes))
        preview_project = self._plan.after.model_copy(deep=True)
        positions = PedigreeLayoutEngine().compute(preview_project, preserve_locked=False)
        for person in preview_project.individuals:
            person.layout.x, person.layout.y = positions[person.id]
        scene = PedigreeScene()
        scene.load_project(preview_project)
        self.preview.setScene(scene)
        self.preview.fitInView(
            scene.pedigree_bounding_rect().adjusted(-80, -60, 80, 80),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.confirmation.setText(
            tr("A migração será aplicada como uma única operação reversível.")
            + "\n\n"
            + "\n".join(self._plan.notes)
        )

    def result_plan(self) -> KinshipPlan:
        self._refresh()
        if self._plan is None:
            raise ValueError(self.impact.text())
        return self._plan

    def accept(self) -> None:
        try:
            self.result_plan()
        except ValueError as error:
            QMessageBox.warning(self, tr("Relação inválida"), tr(str(error)))
            return
        super().accept()


class NewProjectDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Novo projeto"))
        self.setMinimumWidth(500)
        self.name = QLineEdit("Família sem título")
        self.family_id = QLineEdit("RP-001")
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.language = QComboBox()
        self.language.addItem("Português (Brasil)", "pt_BR")
        self.language.addItem("English", "en")
        self.language.setCurrentIndex(max(0, self.language.findData(language_manager.language)))
        self.representation = QComboBox()
        self.representation.addItem("Científica monocromática", "scientific")
        self.representation.addItem("Contornos por categoria", "category_colors")
        self.synthetic = QCheckBox("Iniciar com exemplo sintético (sem dados reais)")
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.form = QFormLayout(self)
        self.form.addRow(
            NexusDialogHeader(
                tr("Novo projeto"),
                tr("Configure o espaço clínico e científico inicial"),
            )
        )
        self.form.addRow("Nome do projeto", self.name)
        self.form.addRow("Identificador familiar", self.family_id)
        self.form.addRow("Descrição opcional", self.description)
        self.form.addRow("Idioma", self.language)
        self.form.addRow("Representação", self.representation)
        self.form.addRow(self.synthetic)
        self.form.addRow(self.buttons)
        language_manager.languageChanged.connect(self.retranslate_ui)
        self.retranslate_ui()

    def retranslate_ui(self, _language=None) -> None:
        self.setWindowTitle(tr("Novo projeto"))
        for widget, text in (
            (self.name, "Nome do projeto"),
            (self.family_id, "Identificador familiar"),
            (self.description, "Descrição opcional"),
            (self.language, "Idioma"),
            (self.representation, "Representação"),
        ):
            label = self.form.labelForField(widget)
            if label is not None:
                label.setText(tr(text))
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("Salvar"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))

    def create_project(self) -> PedigreeProject:
        project = PedigreeProject(
            title=self.name.text().strip() or "Família sem título",
            description=self.description.toPlainText().strip(),
            project_language=self.language.currentData(),
            representation=self.representation.currentData(),
            family={"label": self.family_id.text().strip() or "RP-001"},
        )
        if not self.synthetic.isChecked():
            return project
        root = Individual(label="II-1", gender_identity=GenderIdentity.WOMAN)
        project.individuals.append(root)
        project, _ = FamilyService.add_parents(project, root.id)
        project, partner_id = FamilyService.add_partner(project, root.id)
        project, _ = FamilyService.add_child(project, root.id, partner_id)
        return project
