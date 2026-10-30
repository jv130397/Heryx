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
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)
        self.preview = SymbolPreview()
        root.addWidget(form_widget, 2)
        root.addWidget(self.preview, 1)
        self.symbol_group.buttonClicked.connect(self._update_preview)
        self.phenotype.currentIndexChanged.connect(self._update_preview)
        self.deceased.toggled.connect(self._update_preview)
        self._update_preview()

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
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form = QFormLayout(self)
        form.addRow("Nome do projeto", self.name)
        form.addRow("Identificador familiar", self.family_id)
        form.addRow("Descrição opcional", self.description)
        form.addRow("Idioma", self.language)
        form.addRow("Representação", self.representation)
        form.addRow(self.synthetic)
        form.addRow(buttons)

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
