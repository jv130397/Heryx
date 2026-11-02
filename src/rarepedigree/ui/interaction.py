"""Contextual, presentation-only interaction surfaces over the pedigree canvas."""

from __future__ import annotations

from typing import Any, ClassVar

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsItemGroup,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.domain import GenderIdentity, Individual, ObservationStatus
from rarepedigree.rendering import IndividualItem
from rarepedigree.rendering.items import SYMBOL_SIZE
from rarepedigree.ui.i18n import tr


class RelationPreview:
    """Disposable ghost symbol and connector; never enters the domain model."""

    OFFSETS: ClassVar[dict[str, tuple[float, float]]] = {
        "parents": (0.0, -180.0),
        "father": (-75.0, -180.0),
        "mother": (75.0, -180.0),
        "partner": (150.0, 0.0),
        "child": (0.0, 180.0),
        "adopted_child": (0.0, 180.0),
        "sibling": (-150.0, 0.0),
    }

    def __init__(self, scene: QGraphicsScene) -> None:
        self.scene = scene
        self.group: QGraphicsItemGroup | None = None

    def show(self, source: IndividualItem, action: str) -> None:
        self.clear()
        if action not in self.OFFSETS:
            return
        dx, dy = self.OFFSETS[action]
        start = source.pos()
        end = start + QPoint(int(dx), int(dy))
        pen = QPen(QColor("#8B5CF6"), 2, Qt.PenStyle.DashLine)
        line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
        line.setPen(pen)
        line.setZValue(80)
        ghost_path = QPainterPath()
        half = SYMBOL_SIZE / 2
        ghost_path.addRect(end.x() - half, end.y() - half, SYMBOL_SIZE, SYMBOL_SIZE)
        ghost = QGraphicsPathItem(ghost_path)
        ghost.setPen(pen)
        ghost.setBrush(QBrush(QColor(139, 92, 246, 35)))
        ghost.setZValue(81)
        group = QGraphicsItemGroup()
        self.scene.addItem(group)
        group.addToGroup(line)
        group.addToGroup(ghost)
        self.group = group

    def clear(self) -> None:
        if self.group is not None:
            self.scene.removeItem(self.group)
            self.group = None


class ContextualFamilyBar(QFrame):
    """Floating connection points and family actions for one selected person."""

    actionRequested = Signal(str)
    previewRequested = Signal(str)
    previewCancelled = Signal()
    closeRequested = Signal()

    ACTIONS = (
        ("parents", "↑", "Adicionar ascendentes"),
        ("partner", "↔", "Adicionar parceiro"),
        ("child", "↓", "Adicionar descendente"),
        ("sibling", "⇆", "Adicionar irmão"),
    )

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("context-family-bar")
        self.setFixedSize(330, 118)
        self._buttons: dict[str, QToolButton] = {}
        layout = QGridLayout(self)
        layout.setContentsMargins(8, 5, 8, 7)
        layout.setSpacing(4)
        self.identity = QLabel()
        self.identity.setObjectName("context-person-label")
        close = QToolButton(text="x")
        close.setAccessibleName(tr("Fechar"))
        close.clicked.connect(self.closeRequested)
        layout.addWidget(self.identity, 0, 0, 1, 5)
        layout.addWidget(close, 0, 5)
        for column, (key, symbol, tooltip) in enumerate(self.ACTIONS):
            button = QToolButton(text=symbol)
            button.setProperty("connectionPoint", True)
            button.setToolTip(tr(tooltip))
            button.setAccessibleName(tr(tooltip))
            button.clicked.connect(
                lambda _checked=False, action=key: self.actionRequested.emit(action)
            )
            button.enterEvent = self._enter_handler(button.enterEvent, key)
            button.leaveEvent = self._leave_handler(button.leaveEvent)
            self._buttons[key] = button
            layout.addWidget(button, 1, column)
        edit = QPushButton(tr("Editar"))
        edit.setObjectName("context-edit-button")
        edit.clicked.connect(lambda: self.actionRequested.emit("edit_float"))
        layout.addWidget(edit, 1, 4)
        more = QToolButton(text="⋯")
        more.setToolTip(tr("Mais opções familiares"))
        more.setAccessibleName(tr("Mais opções familiares"))
        more.clicked.connect(lambda: self.actionRequested.emit("advanced"))
        layout.addWidget(more, 1, 5)
        self.animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(160)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.hide()

    def _enter_handler(self, original, key: str):
        def handler(event) -> None:
            self.previewRequested.emit(key)
            original(event)

        return handler

    def _leave_handler(self, original):
        def handler(event) -> None:
            self.previewCancelled.emit()
            original(event)

        return handler

    def set_person(self, person: Individual, allowed: set[str]) -> None:
        self.identity.setText(f"{person.label}  ·  {tr('ações familiares')}")
        for action, button in self._buttons.items():
            button.setVisible(action in allowed or (action == "parents" and "father" in allowed))

    def reveal(self, reduced_motion: bool = False) -> None:
        self.show()
        self.raise_()
        if reduced_motion:
            self.setWindowOpacity(1.0)
            return
        self.animation.stop()
        self.animation.setStartValue(0.35)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.closeRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class FloatingIndividualEditor(QFrame):
    """Compact personal/clinical editor anchored near the selected symbol."""

    saveRequested = Signal(dict)
    closed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("floating-individual-editor")
        self.setFixedSize(410, 430)
        self._person: Individual | None = None
        self._baseline: dict[str, Any] = {}
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        header = QFrame()
        header.setObjectName("floating-editor-header")
        header_layout = QHBoxLayout(header)
        self.title = QLabel()
        close = QToolButton(text="x")
        close.setAccessibleName(tr("Fechar"))
        close.clicked.connect(self.request_close)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(close)
        root.addWidget(header)
        self.tabs = QTabWidget()
        personal = QWidget()
        personal_layout = QGridLayout(personal)
        self.label_edit = QLineEdit()
        self.gender = QComboBox()
        for text, value in (
            ("Homem/menino", GenderIdentity.MAN),
            ("Mulher/menina", GenderIdentity.WOMAN),
            ("Gênero diverso", GenderIdentity.GENDER_DIVERSE),
            ("Não conhecido/especificado", GenderIdentity.UNKNOWN),
        ):
            self.gender.addItem(tr(text), value)
        self.deceased = QCheckBox(tr("Falecido"))
        self.proband = QCheckBox("Proband")
        self.consultand = QCheckBox("Consultand")
        personal_layout.addWidget(QLabel(tr("Identificador exibido")), 0, 0)
        personal_layout.addWidget(self.label_edit, 0, 1)
        personal_layout.addWidget(QLabel(tr("Símbolo/gênero")), 1, 0)
        personal_layout.addWidget(self.gender, 1, 1)
        personal_layout.addWidget(self.deceased, 2, 0, 1, 2)
        personal_layout.addWidget(self.proband, 3, 0, 1, 2)
        personal_layout.addWidget(self.consultand, 4, 0, 1, 2)
        personal_layout.setRowStretch(5, 1)
        clinical = QWidget()
        clinical_layout = QVBoxLayout(clinical)
        clinical_layout.addWidget(QLabel(tr("Estado fenotípico")))
        self.phenotype = QComboBox()
        self.phenotype.addItem(tr("Desconhecido"), ObservationStatus.UNKNOWN)
        self.phenotype.addItem(tr("Afetado"), ObservationStatus.PRESENT)
        self.phenotype.addItem(tr("Não afetado"), ObservationStatus.ABSENT)
        clinical_layout.addWidget(self.phenotype)
        note = QLabel(
            tr(
                "Condições, HPO e resultados genéticos serão habilitados "
                "quando o modelo clínico os suportar."
            )
        )
        note.setWordWrap(True)
        note.setProperty("card", True)
        clinical_layout.addWidget(note)
        clinical_layout.addStretch()
        self.tabs.addTab(personal, tr("Pessoal"))
        self.tabs.addTab(clinical, tr("Clínica"))
        root.addWidget(self.tabs, 1)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton(tr("Cancelar"))
        save = QPushButton(tr("Salvar"))
        save.setObjectName("primary-button")
        cancel.clicked.connect(self.request_close)
        save.clicked.connect(self._save)
        actions.addWidget(cancel)
        actions.addWidget(save)
        root.addLayout(actions)
        self.animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(180)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.hide()

    def set_person(self, person: Individual) -> None:
        self._person = person
        self.title.setText(f"{tr('Editar indivíduo')} · {person.label}")
        self.label_edit.setText(person.label)
        self.gender.setCurrentIndex(max(0, self.gender.findData(person.gender_identity)))
        self.phenotype.setCurrentIndex(max(0, self.phenotype.findData(person.phenotype_status)))
        self.deceased.setChecked(person.deceased)
        self.proband.setChecked(person.proband)
        self.consultand.setChecked(person.consultand)
        self._baseline = self.values()

    def values(self) -> dict[str, Any]:
        return {
            "label": self.label_edit.text().strip() or tr("Indivíduo"),
            "gender_identity": self.gender.currentData(),
            "phenotype_status": self.phenotype.currentData(),
            "deceased": self.deceased.isChecked(),
            "proband": self.proband.isChecked(),
            "consultand": self.consultand.isChecked(),
        }

    def reveal(self, reduced_motion: bool = False) -> None:
        self.show()
        self.raise_()
        if not reduced_motion:
            self.animation.stop()
            self.animation.setStartValue(0.35)
            self.animation.setEndValue(1.0)
            self.animation.start()

    def request_close(self) -> None:
        if self.isVisible() and self.values() != self._baseline:
            answer = QMessageBox.question(
                self,
                tr("Descartar alterações?"),
                tr("Há alterações não salvas neste indivíduo."),
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.hide()
        self.closed.emit()

    def _save(self) -> None:
        values = self.values()
        if not values["label"].strip():
            return
        self.saveRequested.emit(values)
        self._baseline = values
        self.hide()
        self.closed.emit()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.request_close()
            event.accept()
            return
        super().keyPressEvent(event)
