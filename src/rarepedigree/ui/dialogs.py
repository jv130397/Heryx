"""Focused editing and project creation dialogs."""

from typing import Any
from uuid import UUID

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
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
from rarepedigree.ui.i18n import language_manager, tr


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
        painter.setPen(QPen(QColor("#22D3EE"), 4))
        painter.setBrush(
            QColor("#111827") if self.status == ObservationStatus.PRESENT else QColor("white")
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
        root = QHBoxLayout(self)
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
        root.addWidget(form_widget, 2)
        root.addWidget(self.preview, 1)
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


class NewProjectDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Novo projeto")
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
