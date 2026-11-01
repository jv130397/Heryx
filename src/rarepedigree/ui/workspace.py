"""Genomic Nexus navigation widgets layered over the scientific canvas."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.domain import Individual, ObservationStatus, PedigreeProject
from rarepedigree.ui.i18n import tr


class PedigreeMiniMap(QGraphicsView):
    """Live overview of the real scene with a draggable viewport indicator."""

    navigationRequested = Signal(QPointF)

    def __init__(self, scene: QGraphicsScene, source_view: QGraphicsView, parent=None) -> None:
        super().__init__(scene, parent)
        self.source_view = source_view
        self.setObjectName("pedigree-minimap")
        self.setFixedSize(220, 150)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setAccessibleName(tr("Minimapa do heredograma"))
        self._dragging = False

    def refresh(self) -> None:
        bounds = self.scene().itemsBoundingRect().adjusted(-40, -40, 40, 40)
        if not bounds.isEmpty():
            self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
        self.viewport().update()

    def visible_scene_rect(self) -> QRectF:
        return self.source_view.mapToScene(self.source_view.viewport().rect()).boundingRect()

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawForeground(painter, rect)
        visible = self.visible_scene_rect()
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = painter.pen()
        pen.setColor(QColor("#078FC2"))
        pen.setWidthF(2 / max(self.transform().m11(), 0.01))
        painter.setPen(pen)
        painter.drawRect(visible)
        painter.restore()

    def _navigate(self, position: QPoint) -> None:
        point = self.mapToScene(position)
        self.navigationRequested.emit(point)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._navigate(event.position().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self._navigate(event.position().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)


class IndividualSearch(QFrame):
    """Responsive in-memory search for people in the active project."""

    personActivated = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("individual-search")
        self.setFixedHeight(300)
        self._project = PedigreeProject()
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)
        header = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setPlaceholderText(tr("Buscar indivíduo, parentesco ou UUID…"))
        self.query.setClearButtonEnabled(True)
        self.query.setAccessibleName(tr("Buscar indivíduos"))
        self.advanced = QToolButton(text="UUID")
        self.advanced.setCheckable(True)
        self.close_button = QToolButton(text="x")
        header.addWidget(self.query, 1)
        header.addWidget(self.advanced)
        header.addWidget(self.close_button)
        self.results = QListWidget()
        self.results.setMaximumHeight(220)
        root.addLayout(header)
        root.addWidget(self.results)
        self.query.textChanged.connect(self._filter)
        self.advanced.toggled.connect(lambda _checked: self._filter(self.query.text()))
        self.results.itemActivated.connect(self._activate)
        self.results.itemClicked.connect(self._activate)

    def retranslate_ui(self) -> None:
        self.query.setPlaceholderText(tr("Buscar indivíduo, parentesco ou UUID…"))
        self.query.setAccessibleName(tr("Buscar indivíduos"))
        self.setAccessibleName(tr("Busca de indivíduos"))

    def set_project(
        self,
        project: PedigreeProject,
        kinship_label: Callable[[Individual], str] | None = None,
    ) -> None:
        self._project = project
        self._kinship_label = kinship_label
        self._filter(self.query.text())

    def _filter(self, text: str) -> None:
        needle = text.strip().casefold()
        self.results.clear()
        for person in self._project.individuals:
            kinship = self._kinship_label(person) if getattr(self, "_kinship_label", None) else ""
            phenotype = person.phenotype_status.value
            fields = [person.label, kinship, phenotype]
            if self.advanced.isChecked():
                fields.append(str(person.id))
            if needle and not any(needle in field.casefold() for field in fields):
                continue
            state = {
                ObservationStatus.PRESENT: tr("afetado"),
                ObservationStatus.ABSENT: tr("não afetado"),
                ObservationStatus.UNKNOWN: tr("desconhecido"),
            }[person.phenotype_status]
            item = QListWidgetItem(f"{person.label}  ·  {kinship or state}")
            item.setData(Qt.ItemDataRole.UserRole, person.id)
            item.setToolTip(str(person.id))
            self.results.addItem(item)
            # The complete project is searched, but only a useful viewport-sized
            # result page is materialized. This keeps 200+ person pedigrees fast.
            limit = 20 if not needle else 50
            if self.results.count() >= limit:
                break
        if self.results.count():
            self.results.setCurrentRow(0)

    def _activate(self, item: QListWidgetItem) -> None:
        self.personActivated.emit(item.data(Qt.ItemDataRole.UserRole))


class ViewModeControl(QWidget):
    modeChanged = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("view-mode-control")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        self.label = QLabel(tr("Visão"))
        layout.addWidget(self.label)
        self.combo = QComboBox()
        self.combo.addItem(tr("Geral"), "overview")
        self.combo.addItem(tr("Focada"), "focused")
        self.combo.addItem(tr("Científica"), "scientific")
        self.combo.currentIndexChanged.connect(
            lambda _index: self.modeChanged.emit(self.combo.currentData())
        )
        layout.addWidget(self.combo)

    def retranslate_ui(self) -> None:
        self.label.setText(tr("Visão"))
        for index, source in enumerate(("Geral", "Focada", "Científica")):
            self.combo.setItemText(index, tr(source))

    def set_mode(self, mode: str) -> None:
        index = self.combo.findData(mode)
        if index >= 0:
            self.combo.setCurrentIndex(index)
