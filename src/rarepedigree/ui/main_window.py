"""Main desktop window for the Phase 4 functional prototype."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QPointF, QSettings, Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QPainter, QUndoStack
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.application import (
    AddIndividualCommand,
    AddRelationshipCommand,
    MoveIndividualCommand,
    ReplaceProjectCommand,
    UpdateIndividualCommand,
)
from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    LayoutPosition,
    ParentageKind,
    PedigreeProject,
    Relationship,
    RelationshipKind,
    TwinZygosity,
)
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.rendering import IndividualItem, PedigreeScene, PedigreeView
from rarepedigree.rendering.exporters import ExportOptions, export_pdf, export_png, export_svg
from rarepedigree.ui.preferences import PreferencesDialog
from rarepedigree.ui.properties import PropertiesPanel
from rarepedigree.ui.theme import SCIENTIFIC_WORKSPACE_STYLESHEET


class MainWindow(QMainWindow):
    """Editor shell whose commands keep project data and scene synchronized."""

    def __init__(self) -> None:
        super().__init__()
        self.project = PedigreeProject()
        self.repository = JsonProjectRepository()
        self.current_path: Path | None = None
        self.undo_stack = QUndoStack(self)
        self.undo_stack.indexChanged.connect(lambda _index: self._update_title())
        self.layout_engine = PedigreeLayoutEngine()
        self.settings = QSettings()
        self.setStyleSheet(SCIENTIFIC_WORKSPACE_STYLESHEET)

        self.scene = PedigreeScene()
        self.scene.on_person_moved = self._on_person_moved
        self.scene.on_context_action = self._context_action
        self.scene.selectionChanged.connect(self._selection_changed)
        self.view = PedigreeView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(PedigreeView.DragMode.RubberBandDrag)
        self.setCentralWidget(self.view)

        self.properties = PropertiesPanel(self._apply_properties)
        dock = QDockWidget("Propriedades do indivíduo", self)
        dock.setObjectName("individual-properties")
        dock.setWidget(self.properties)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_toolbox()
        self._update_title()
        self.resize(1180, 760)
        self.statusBar().showMessage("Scientific Workspace — dados locais, sem telemetria")

    def _create_actions(self) -> None:
        self.new_action = QAction("Novo", self, shortcut=QKeySequence.StandardKey.New)
        self.open_action = QAction("Abrir…", self, shortcut=QKeySequence.StandardKey.Open)
        self.save_action = QAction("Salvar", self, shortcut=QKeySequence.StandardKey.Save)
        self.save_as_action = QAction(
            "Salvar como…", self, shortcut=QKeySequence.StandardKey.SaveAs
        )
        self.export_action = QAction("Exportar figura…", self, shortcut="Ctrl+E")
        self.quit_action = QAction("Sair", self, shortcut=QKeySequence.StandardKey.Quit)
        self.undo_action = self.undo_stack.createUndoAction(self, "Desfazer")
        self.redo_action = self.undo_stack.createRedoAction(self, "Refazer")
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.add_man_action = QAction("Adicionar homem/menino", self)
        self.add_woman_action = QAction("Adicionar mulher/menina", self)
        self.add_unspecified_action = QAction("Adicionar gênero não especificado", self)
        self.relationship_action = QAction("Relacionar selecionados", self)
        self.consanguinity_action = QAction("Relação consanguínea", self)
        self.separation_action = QAction("Relação separada", self)
        self.divorce_action = QAction("Relação divorciada", self)
        self.add_parents_action = QAction("Adicionar pais", self)
        self.add_partner_action = QAction("Adicionar parceiro", self)
        self.add_child_action = QAction("Adicionar filho", self)
        self.add_sibling_action = QAction("Adicionar irmão", self)
        self.delete_action = QAction("Excluir", self, shortcut=QKeySequence.StandardKey.Delete)
        self.auto_layout_action = QAction("Organização automática", self, shortcut="Ctrl+L")
        self.fit_action = QAction("Ajustar à tela", self, shortcut="Ctrl+0")
        self.preferences_action = QAction("Preferências…", self)
        self.twins_mz_action = QAction("Marcar selecionados como gêmeos monozigóticos", self)
        self.twins_dz_action = QAction("Marcar selecionados como gêmeos dizigóticos", self)
        self.zoom_in_action = QAction("Ampliar", self, shortcut=QKeySequence.StandardKey.ZoomIn)
        self.zoom_out_action = QAction("Reduzir", self, shortcut=QKeySequence.StandardKey.ZoomOut)

        self.new_action.triggered.connect(self.new_project)
        self.open_action.triggered.connect(self.open_project)
        self.save_action.triggered.connect(self.save_project)
        self.save_as_action.triggered.connect(self.save_project_as)
        self.export_action.triggered.connect(self.export_figure)
        self.quit_action.triggered.connect(self.close)
        self.add_man_action.triggered.connect(lambda: self.add_person(GenderIdentity.MAN))
        self.add_woman_action.triggered.connect(lambda: self.add_person(GenderIdentity.WOMAN))
        self.add_unspecified_action.triggered.connect(
            lambda: self.add_person(GenderIdentity.UNKNOWN)
        )
        self.relationship_action.triggered.connect(
            lambda: self.add_relationship(RelationshipKind.PARTNERSHIP)
        )
        self.consanguinity_action.triggered.connect(
            lambda: self.add_relationship(RelationshipKind.CONSANGUINEOUS_PARTNERSHIP)
        )
        self.separation_action.triggered.connect(
            lambda: self.add_relationship(RelationshipKind.SEPARATED_PARTNERSHIP)
        )
        self.divorce_action.triggered.connect(
            lambda: self.add_relationship(RelationshipKind.DIVORCED_PARTNERSHIP)
        )
        self.add_parents_action.triggered.connect(lambda: self._context_for_selected("parents"))
        self.add_partner_action.triggered.connect(lambda: self._context_for_selected("partner"))
        self.add_child_action.triggered.connect(lambda: self._context_for_selected("child"))
        self.add_sibling_action.triggered.connect(lambda: self._context_for_selected("sibling"))
        self.delete_action.triggered.connect(lambda: self._context_for_selected("delete"))
        self.auto_layout_action.triggered.connect(self.auto_layout)
        self.fit_action.triggered.connect(self.fit_pedigree)
        self.preferences_action.triggered.connect(lambda: PreferencesDialog(self).exec())
        self.twins_mz_action.triggered.connect(
            lambda: self._set_selected_twins(TwinZygosity.MONOZYGOTIC)
        )
        self.twins_dz_action.triggered.connect(
            lambda: self._set_selected_twins(TwinZygosity.DIZYGOTIC)
        )
        self.zoom_in_action.triggered.connect(lambda: self.view.scale(1.2, 1.2))
        self.zoom_out_action.triggered.connect(lambda: self.view.scale(1 / 1.2, 1 / 1.2))

    def _create_menus(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        file_menu.addActions(
            [
                self.new_action,
                self.open_action,
                self.save_action,
                self.save_as_action,
                self.export_action,
            ]
        )
        file_menu.addSeparator()
        file_menu.addAction(self.preferences_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)
        edit_menu = self.menuBar().addMenu("Editar")
        edit_menu.addActions([self.undo_action, self.redo_action])
        pedigree_menu = self.menuBar().addMenu("Heredograma")
        pedigree_menu.addActions(
            [
                self.add_man_action,
                self.add_woman_action,
                self.add_unspecified_action,
                self.relationship_action,
                self.consanguinity_action,
                self.separation_action,
                self.divorce_action,
                self.add_parents_action,
                self.add_partner_action,
                self.add_child_action,
                self.add_sibling_action,
                self.delete_action,
                self.twins_mz_action,
                self.twins_dz_action,
            ]
        )
        view_menu = self.menuBar().addMenu("Exibir")
        view_menu.addActions([self.zoom_in_action, self.zoom_out_action])
        view_menu.addActions([self.fit_action, self.auto_layout_action])

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Ferramentas principais", self)
        toolbar.setObjectName("main-toolbar")
        toolbar.addActions(
            [
                self.new_action,
                self.open_action,
                self.save_action,
                self.undo_action,
                self.redo_action,
                self.auto_layout_action,
                self.export_action,
                self.preferences_action,
            ]
        )
        toolbar.addSeparator()
        toolbar.addActions(
            [
                self.add_man_action,
                self.add_woman_action,
                self.add_unspecified_action,
                self.relationship_action,
            ]
        )
        self.addToolBar(toolbar)

    def _create_toolbox(self) -> None:
        dock = QDockWidget("Ferramentas", self)
        dock.setObjectName("scientific-tools")
        panel = QWidget()
        layout = QVBoxLayout(panel)
        title = QLabel("RAREPEDIGREE\nSCIENTIFIC WORKSPACE")
        title.setStyleSheet("font-weight: bold; color: #35c5e8; padding: 8px;")
        layout.addWidget(title)
        for action in (
            self.add_unspecified_action,
            self.add_parents_action,
            self.add_partner_action,
            self.add_child_action,
            self.add_sibling_action,
            self.relationship_action,
            self.auto_layout_action,
            self.fit_action,
            self.delete_action,
        ):
            button = QPushButton(action.text())
            button.clicked.connect(action.trigger)
            layout.addWidget(button)
        layout.addStretch()
        dock.setWidget(panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def new_project(self) -> None:
        if not self._may_discard_changes():
            return
        self.project = PedigreeProject()
        self.current_path = None
        self.undo_stack.clear()
        self.scene.load_project(self.project)
        self._update_title()

    def _apply_project(self, project: PedigreeProject) -> None:
        self.project = project
        self.scene.load_project(project)
        self._update_title()

    def _context_for_selected(self, action: str) -> None:
        selected = self.scene.selected_people()
        if not selected:
            QMessageBox.information(self, "Família", "Selecione um indivíduo.")
            return
        self._context_action(selected[0], action)

    def _context_action(self, item: IndividualItem, action: str) -> None:
        before = self.project.model_copy(deep=True)
        try:
            if action == "parents":
                after, _ = FamilyService.add_parents(before, item.person.id)
                label = "Adicionar pais"
            elif action == "unknown_parents":
                after, _ = FamilyService.add_parents(before, item.person.id, unknown=True)
                label = "Adicionar pais desconhecidos"
            elif action == "partner":
                after, _ = FamilyService.add_partner(before, item.person.id)
                label = "Adicionar parceiro"
            elif action == "child":
                selected = self.scene.selected_people()
                partner_id = (
                    selected[1].person.id
                    if len(selected) == 2 and selected[0].person.id == item.person.id
                    else selected[0].person.id
                    if len(selected) == 2 and selected[1].person.id == item.person.id
                    else None
                )
                after, _ = FamilyService.add_child(before, item.person.id, partner_id)
                label = "Adicionar filho"
            elif action == "adopted_child":
                after, _ = FamilyService.add_child(
                    before, item.person.id, kind=ParentageKind.LEGAL
                )
                label = "Adicionar filho adotivo"
            elif action == "sibling":
                after, _ = FamilyService.add_sibling(before, item.person.id)
                label = "Adicionar irmão"
            elif action == "delete":
                after = FamilyService.delete_individual(before, item.person.id)
                label = "Excluir indivíduo"
            else:
                return
        except ValueError as error:
            QMessageBox.warning(self, "Relação inválida", str(error))
            return
        positions = self.layout_engine.compute(after)
        for person in after.individuals:
            person.layout.x, person.layout.y = positions[person.id]
        self.undo_stack.push(ReplaceProjectCommand(label, before, after, self._apply_project))
        self.fit_pedigree()

    def auto_layout(self, push_undo: bool = True) -> None:
        before = self.project.model_copy(deep=True)
        after = self.project.model_copy(deep=True)
        positions = self.layout_engine.compute(after)
        for person in after.individuals:
            person.layout.x, person.layout.y = positions[person.id]
        if push_undo:
            self.undo_stack.push(
                ReplaceProjectCommand("Organização automática", before, after, self._apply_project)
            )
        else:
            self._apply_project(after)
        self.fit_pedigree()

    def _set_selected_twins(self, zygosity: TwinZygosity) -> None:
        selected = self.scene.selected_people()
        try:
            after = FamilyService.set_twins(
                self.project, [item.person.id for item in selected], zygosity
            )
        except ValueError as error:
            QMessageBox.warning(self, "Gêmeos", str(error))
            return
        self.undo_stack.push(
            ReplaceProjectCommand(
                "Definir grupo de gêmeos", self.project, after, self._apply_project
            )
        )

    def fit_pedigree(self) -> None:
        rect = self.scene.itemsBoundingRect().adjusted(-80, -80, 80, 80)
        if not rect.isEmpty():
            self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def add_person(self, gender: GenderIdentity) -> Individual:
        count = len(self.project.individuals)
        center = self.view.mapToScene(self.view.viewport().rect().center())
        person = Individual(
            label=f"I-{count + 1}",
            gender_identity=gender,
            layout=LayoutPosition(x=center.x() + (count % 5) * 75, y=center.y()),
        )
        self.undo_stack.push(AddIndividualCommand(self.project, self.scene, person))
        self.scene.clearSelection()
        self.scene.person_items[person.id].setSelected(True)
        return person

    def add_relationship(self, kind: RelationshipKind) -> Relationship | None:
        selected = self.scene.selected_people()
        if len(selected) != 2:
            QMessageBox.information(self, "Relação", "Selecione exatamente dois indivíduos.")
            return None
        member_ids = {selected[0].person.id, selected[1].person.id}
        if any(
            {relationship.member_a, relationship.member_b} == member_ids
            for relationship in self.project.relationships
        ):
            QMessageBox.information(self, "Relação", "Esses indivíduos já possuem uma relação.")
            return None
        relationship = Relationship(
            member_a=selected[0].person.id,
            member_b=selected[1].person.id,
            kind=kind,
        )
        self.undo_stack.push(AddRelationshipCommand(self.project, self.scene, relationship))
        return relationship

    def _on_person_moved(
        self, item: IndividualItem, old_position: QPointF, new_position: QPointF
    ) -> None:
        self.undo_stack.push(
            MoveIndividualCommand(self.scene, item, old_position, new_position)
        )

    def _selection_changed(self) -> None:
        try:
            selected = self.scene.selected_people()
        except RuntimeError:
            return
        self.properties.set_item(selected[0] if len(selected) == 1 else None)

    def _apply_properties(self, item: IndividualItem, new_values: dict[str, Any]) -> None:
        old_values = {field: getattr(item.person, field) for field in new_values}
        if old_values != new_values:
            self.undo_stack.push(UpdateIndividualCommand(item, old_values, new_values))

    def _sync_layout(self) -> None:
        for item in self.scene.person_items.values():
            item.person.layout.x = item.pos().x()
            item.person.layout.y = item.pos().y()

    def save_project(self) -> bool:
        if self.current_path is None:
            return self.save_project_as()
        return self._save_to(self.current_path)

    def save_project_as(self) -> bool:
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar projeto",
            "heredograma.rps.json",
            "RarePedigree (*.rps.json);;JSON (*.json)",
        )
        return bool(filename) and self._save_to(Path(filename))

    def _save_to(self, path: Path) -> bool:
        try:
            self._sync_layout()
            self.repository.save(self.project, path)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Falha ao salvar", str(error))
            return False
        self.current_path = path
        self.undo_stack.setClean()
        self._update_title()
        self.statusBar().showMessage(f"Projeto salvo em {path}", 5000)
        return True

    def open_project(self) -> None:
        if not self._may_discard_changes():
            return
        filename, _ = QFileDialog.getOpenFileName(
            self, "Abrir projeto", "", "RarePedigree (*.rps.json *.json)"
        )
        if filename:
            self.load_from(Path(filename))

    def load_from(self, path: Path) -> bool:
        try:
            project = self.repository.load(path)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Projeto inválido", str(error))
            return False
        self.project = project
        self.current_path = path
        self.undo_stack.clear()
        self.scene.load_project(project)
        self.undo_stack.setClean()
        self._update_title()
        return True

    def export_figure(self) -> None:
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exportar figura",
            "heredograma.svg",
            "SVG vetorial (*.svg);;PNG (*.png);;PDF (*.pdf)",
        )
        if not filename:
            return
        path = Path(filename)
        options = ExportOptions(
            png_scale=self.settings.value("export/png_scale", 2, int),
            margin=self.settings.value("export/margin", 30, int),
            landscape=self.settings.value("export/landscape", True, bool),
        )
        try:
            if "PNG" in selected_filter or path.suffix.lower() == ".png":
                export_png(self.scene, path, options)
            elif "PDF" in selected_filter or path.suffix.lower() == ".pdf":
                export_pdf(self.scene, path, options)
            else:
                export_svg(self.scene, path, options)
        except OSError as error:
            QMessageBox.critical(self, "Falha na exportação", str(error))
            return
        self.statusBar().showMessage(f"Figura exportada para {path}", 5000)

    def _update_title(self) -> None:
        filename = self.current_path.name if self.current_path else "Sem título"
        dirty = " *" if not self.undo_stack.isClean() else ""
        self.setWindowTitle(f"{filename}{dirty} — RarePedigree Scientific Workspace")

    def _may_discard_changes(self) -> bool:
        if self.undo_stack.isClean() or not self.isVisible():
            return True
        choice = QMessageBox.question(
            self,
            "Alterações não salvas",
            "Descartar as alterações não salvas?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return choice == QMessageBox.StandardButton.Discard

    def closeEvent(self, event: QCloseEvent) -> None:
        event.accept() if self._may_discard_changes() else event.ignore()
