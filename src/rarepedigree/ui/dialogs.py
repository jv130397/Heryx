"""Focused editing and project creation dialogs."""

from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    ObservationStatus,
    PedigreeProject,
    SiblingKind,
)
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
        return self.kind.currentData()

    def sibling_label(self) -> str | None:
        return self.name.text().strip() or None


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
