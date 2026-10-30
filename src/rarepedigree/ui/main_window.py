"""Main desktop window for the Phase 4 functional prototype."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from PySide6.QtCore import QPointF, QSettings, QSize, Qt
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QCloseEvent,
    QFont,
    QKeySequence,
    QPainter,
    QResizeEvent,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedLayout,
    QToolBar,
    QToolButton,
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
from rarepedigree.rendering.style import PedigreeRenderStyle
from rarepedigree.ui.components import (
    EmptyState,
    FamilyMenu,
    SlidingPanel,
    Toast,
    ToolRailButton,
    ZoomControl,
)
from rarepedigree.ui.dialogs import EditIndividualDialog, NewProjectDialog
from rarepedigree.ui.i18n import language_manager, tr
from rarepedigree.ui.icons import icon
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
        self.undo_stack.indexChanged.connect(self._undo_index_changed)
        self.layout_engine = PedigreeLayoutEngine()
        self.settings = QSettings()
        self.setStyleSheet(SCIENTIFIC_WORKSPACE_STYLESHEET)
        language_manager.languageChanged.connect(self.retranslate_ui)
        self._create_actions()

        self.scene = PedigreeScene()
        self.scene.on_person_moved = self._on_person_moved
        self.scene.on_context_action = self._context_action
        self.scene.context_actions = self._available_context_actions
        self.scene.selectionChanged.connect(self._selection_changed)
        self.view = PedigreeView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(PedigreeView.DragMode.RubberBandDrag)
        self.empty_state = EmptyState()
        self.empty_state.addRequested.connect(lambda: self.add_person(GenderIdentity.UNKNOWN))
        self.empty_overlay = QWidget()
        empty_layout = QVBoxLayout(self.empty_overlay)
        empty_layout.setContentsMargins(24, 24, 24, 24)
        empty_layout.addWidget(
            self.empty_state,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        canvas = QWidget()
        self.canvas_stack = QStackedLayout(canvas)
        self.canvas_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.canvas_stack.setContentsMargins(0, 0, 0, 0)
        self.canvas_stack.addWidget(self.view)
        self.canvas_stack.addWidget(self.empty_overlay)
        self.toast = Toast(canvas)
        self.central_shell = QWidget()
        self.central_layout = QHBoxLayout(self.central_shell)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        self.tool_rail = self._create_toolbox()
        self.central_layout.addWidget(self.tool_rail)
        self.central_layout.addWidget(canvas, 1)
        self.setCentralWidget(self.central_shell)

        self.properties = PropertiesPanel(self._apply_properties)
        self.properties.editRequested.connect(lambda: self._context_for_selected("edit_dialog"))
        self.properties_drawer = SlidingPanel(self.properties, self.central_shell)
        self.properties_drawer.closeRequested.connect(self.scene.clearSelection)
        # Compatibility alias for callers that previously adjusted the dock.
        self.properties_dock = self.properties_drawer

        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        self._update_title()
        self.resize(1440, 900)
        self._update_workspace_state()
        self.apply_preferences()
        self.retranslate_ui()

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
        self.move_action = QAction("Mover", self)
        self.move_action.setCheckable(True)
        self.twins_mz_action = QAction("Marcar selecionados como gêmeos monozigóticos", self)
        self.twins_dz_action = QAction("Marcar selecionados como gêmeos dizigóticos", self)
        self.zoom_in_action = QAction("Ampliar", self, shortcut=QKeySequence.StandardKey.ZoomIn)
        self.zoom_out_action = QAction("Reduzir", self, shortcut=QKeySequence.StandardKey.ZoomOut)
        self.edit_action = QAction("Editar indivíduo", self, shortcut="Ctrl+I")
        self.language_action = QAction("PT", self)
        self.select_action = QAction("Selecionar", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True)
        self.tool_mode_group = QActionGroup(self)
        self.tool_mode_group.setExclusive(True)
        self.tool_mode_group.addAction(self.select_action)
        self.tool_mode_group.addAction(self.move_action)

        action_icons = {
            self.new_action: "new",
            self.open_action: "open",
            self.save_action: "save",
            self.undo_action: "undo",
            self.redo_action: "redo",
            self.auto_layout_action: "layout",
            self.export_action: "export",
            self.preferences_action: "settings",
            self.add_unspecified_action: "person",
            self.relationship_action: "link",
            self.delete_action: "delete",
            self.fit_action: "fit",
            self.zoom_in_action: "zoom_in",
            self.edit_action: "person",
            self.move_action: "move",
        }
        for action, name in action_icons.items():
            action.setIcon(icon(name))
            shortcut = action.shortcut().toString()
            action.setToolTip(f"{action.text()}" + (f" ({shortcut})" if shortcut else ""))

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
        self.preferences_action.triggered.connect(self.open_preferences)
        self.twins_mz_action.triggered.connect(
            lambda: self._set_selected_twins(TwinZygosity.MONOZYGOTIC)
        )
        self.twins_dz_action.triggered.connect(
            lambda: self._set_selected_twins(TwinZygosity.DIZYGOTIC)
        )
        self.zoom_in_action.triggered.connect(
            lambda: self.view.set_zoom(self.view.zoom_percent + 20)
        )
        self.zoom_out_action.triggered.connect(
            lambda: self.view.set_zoom(self.view.zoom_percent - 20)
        )
        self.edit_action.triggered.connect(lambda: self._context_for_selected("edit_dialog"))
        self.language_action.triggered.connect(self.toggle_language)
        self.select_action.triggered.connect(lambda: self._set_interaction_mode("select"))
        self.move_action.triggered.connect(lambda: self._set_interaction_mode("move"))

    def _create_menus(self) -> None:
        self.file_menu = self.menuBar().addMenu("Arquivo")
        self.file_menu.addActions(
            [
                self.new_action,
                self.open_action,
                self.save_action,
                self.save_as_action,
                self.export_action,
            ]
        )
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.preferences_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.quit_action)
        self.edit_menu = self.menuBar().addMenu("Editar")
        self.edit_menu.addActions([self.undo_action, self.redo_action])
        self.pedigree_menu = self.menuBar().addMenu("Heredograma")
        self.pedigree_menu.addActions(
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
                self.edit_action,
                self.twins_mz_action,
                self.twins_dz_action,
            ]
        )
        self.view_menu = self.menuBar().addMenu("Exibir")
        self.view_menu.addActions([self.zoom_in_action, self.zoom_out_action])
        self.view_menu.addActions([self.fit_action, self.auto_layout_action])

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Ferramentas principais", self)
        toolbar.setObjectName("main-toolbar")
        toolbar.setIconSize(QSize(19, 19))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        brand = QLabel("RAREPEDIGREE")
        brand.setStyleSheet(
            "font-weight: 800; color: #67E8F9; letter-spacing: 1px; padding-right: 10px;"
        )
        toolbar.addWidget(brand)
        toolbar.addSeparator()
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
                self.language_action,
            ]
        )
        toolbar.addSeparator()
        self.project_title_label = QLabel("Sem título")
        self.project_title_label.setStyleSheet("font-weight: 600; padding: 0 8px;")
        toolbar.addWidget(self.project_title_label)
        self.dirty_label = QLabel("SALVO")
        self.dirty_label.setStyleSheet("color: #94A3B8; font-size: 10px; padding: 3px 6px;")
        toolbar.addWidget(self.dirty_label)
        self.addToolBar(toolbar)

    def _create_toolbox(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("tool-rail")
        panel.setFixedWidth(210)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(7, 10, 7, 10)
        layout.setSpacing(5)
        self.rail_buttons: list[QToolButton] = []
        self.rail_expanded = True
        self.collapse_action = QAction("«", self)
        self.collapse_action.triggered.connect(self.toggle_tool_rail)
        self.collapse_button = ToolRailButton(self.collapse_action, "fit", expanded=True)
        layout.addWidget(self.collapse_button)
        select_button = ToolRailButton(self.select_action, "select", expanded=True)
        self.rail_buttons.append(select_button)
        layout.addWidget(select_button)
        self.person_button = QToolButton()
        person_button = self.person_button
        person_button.setIcon(icon("person"))
        person_button.setText("Adicionar indivíduo")
        person_button.setFixedHeight(46)
        person_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        person_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        person_menu = FamilyMenu(
            [self.add_man_action, self.add_woman_action, self.add_unspecified_action],
            person_button,
        )
        person_button.setMenu(person_menu)
        layout.addWidget(person_button)
        self.family_button = QToolButton()
        family_button = self.family_button
        family_button.setIcon(icon("family"))
        family_button.setFixedHeight(46)
        family_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        family_button.setText("Adicionar familiar")
        family_button.setProperty("railButton", True)
        family_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        family_button.setMenu(
            FamilyMenu(
                [
                    self.add_parents_action,
                    self.add_partner_action,
                    self.add_child_action,
                    self.add_sibling_action,
                ],
                family_button,
            )
        )
        family_button.menu().addSeparator()
        family_button.menu().addAction("Adicionar pais desconhecidos").triggered.connect(
            lambda: self._context_for_selected("unknown_parents")
        )
        family_button.menu().addAction("Adicionar filho adotivo").triggered.connect(
            lambda: self._context_for_selected("adopted_child")
        )
        family_button.setToolTip("Adicionar familiar")
        family_button.setAccessibleName("Adicionar familiar")
        layout.addWidget(family_button)
        self.rail_buttons.extend([person_button, family_button])
        for action, icon_name in [
            (self.relationship_action, "link"),
            (self.move_action, "move"),
            (self.auto_layout_action, "layout"),
        ]:
            button = ToolRailButton(action, icon_name, expanded=True)
            self.rail_buttons.append(button)
            layout.addWidget(button)
        layout.addStretch()
        for action, icon_name in [(self.fit_action, "fit"), (self.delete_action, "delete")]:
            button = ToolRailButton(action, icon_name, expanded=True)
            self.rail_buttons.append(button)
            layout.addWidget(button)
        return panel

    def toggle_tool_rail(self) -> None:
        self.rail_expanded = not self.rail_expanded
        self.tool_rail.setFixedWidth(210 if self.rail_expanded else 60)
        style = (
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            if self.rail_expanded
            else Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        for button in self.rail_buttons:
            button.setToolButtonStyle(style)
        self.collapse_action.setText("«" if self.rail_expanded else "»")

    def _set_interaction_mode(self, mode: str) -> None:
        self.scene.set_interaction_mode(mode)
        self.view.setDragMode(
            PedigreeView.DragMode.NoDrag
            if mode == "move"
            else PedigreeView.DragMode.RubberBandDrag
        )
        cursor = Qt.CursorShape.OpenHandCursor if mode == "move" else Qt.CursorShape.ArrowCursor
        self.view.viewport().setCursor(cursor)

    def _create_statusbar(self) -> None:
        self.count_status = QLabel()
        self.generation_status = QLabel()
        self.save_status = QLabel("Salvo")
        self.message_status = QLabel("Pronto")
        self.zoom_control = ZoomControl()
        self.floating_zoom = ZoomControl(self.view.viewport())
        self.view.floating_control = self.floating_zoom
        self.zoom_control.zoomIn.connect(self.zoom_in_action.trigger)
        self.zoom_control.zoomOut.connect(self.zoom_out_action.trigger)
        self.zoom_control.fitRequested.connect(self.fit_action.trigger)
        self.floating_zoom.zoomIn.connect(self.zoom_in_action.trigger)
        self.floating_zoom.zoomOut.connect(self.zoom_out_action.trigger)
        self.floating_zoom.fitRequested.connect(self.fit_action.trigger)
        self.view.zoomChanged.connect(self.zoom_control.set_zoom)
        self.view.zoomChanged.connect(self.floating_zoom.set_zoom)
        self.statusBar().addWidget(self.message_status, 1)
        self.statusBar().addPermanentWidget(self.count_status)
        self.statusBar().addPermanentWidget(self.generation_status)
        self.statusBar().addPermanentWidget(self.save_status)
        self.statusBar().addPermanentWidget(self.zoom_control)

    def new_project(self) -> None:
        if not self._may_discard_changes():
            return
        dialog = NewProjectDialog(self)
        if self.isVisible() and dialog.exec() != dialog.DialogCode.Accepted:
            return
        self.project = dialog.create_project() if self.isVisible() else PedigreeProject()
        if self.project.individuals:
            positions = self.layout_engine.compute(self.project)
            for person in self.project.individuals:
                person.layout.x, person.layout.y = positions[person.id]
        self.current_path = None
        self.undo_stack.clear()
        self.scene.load_project(self.project)
        self._update_workspace_state()
        if self.project.individuals:
            self.fit_pedigree()

    def _apply_project(self, project: PedigreeProject) -> None:
        self.project = project
        self.scene.load_project(project)
        self._update_workspace_state()

    def _context_for_selected(self, action: str) -> None:
        selected = self.scene.selected_people()
        if not selected:
            QMessageBox.information(self, "Família", "Selecione um indivíduo.")
            return
        if action == "delete" and self.isVisible():
            choice = QMessageBox.question(
                self,
                "Excluir indivíduo",
                "Excluir o indivíduo selecionado e suas relações dependentes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if choice != QMessageBox.StandardButton.Yes:
                return
        self._context_action(selected[0], action)

    def _context_action(self, item: IndividualItem, action: str) -> None:
        if action == "edit":
            self.scene.clearSelection()
            item.setSelected(True)
            self.properties.label_edit.setFocus()
            return
        if action == "edit_dialog":
            dialog = EditIndividualDialog(item.person, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                values = dialog.values()
                old_values = {field: getattr(item.person, field) for field in values}
                if values != old_values:
                    self.undo_stack.push(UpdateIndividualCommand(item, old_values, values))
                    self.properties.set_item(item, self.project)
                    self.message_status.setText("Indivíduo atualizado")
            return
        before = self.project.model_copy(deep=True)
        try:
            if action == "parents":
                after, _ = FamilyService.add_parents(before, item.person.id)
                label = "Adicionar pais"
            elif action == "father":
                after, _ = FamilyService.add_parent(before, item.person.id, GenderIdentity.MAN)
                label = "Adicionar pai"
            elif action == "mother":
                after, _ = FamilyService.add_parent(before, item.person.id, GenderIdentity.WOMAN)
                label = "Adicionar mãe"
            elif action == "unknown_parents":
                after, _ = FamilyService.add_parents(before, item.person.id, unknown=True)
                label = "Adicionar pais desconhecidos"
            elif action == "partner":
                after, _ = FamilyService.add_partner(before, item.person.id)
                label = "Adicionar parceiro"
            elif action == "child":
                selected = self.scene.selected_people()
                partner_id = self._partner_for_new_child(item.person.id, selected)
                after, _ = FamilyService.add_child(before, item.person.id, partner_id)
                label = "Adicionar filho"
            elif action == "adopted_child":
                after, _ = FamilyService.add_child(
                    before,
                    item.person.id,
                    self._partner_for_new_child(item.person.id, self.scene.selected_people()),
                    kind=ParentageKind.LEGAL,
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
        self.message_status.setText(tr(label))
        self.toast.show_message(tr(label))
        self.fit_pedigree()

    def _partner_for_new_child(
        self, person_id: UUID, selected: list[IndividualItem]
    ) -> UUID | None:
        selected_partner = next(
            (entry.person.id for entry in selected if entry.person.id != person_id), None
        )
        partners = [
            relation.member_b if relation.member_a == person_id else relation.member_a
            for relation in self.project.relationships
            if person_id in {relation.member_a, relation.member_b}
        ]
        if selected_partner is not None:
            if selected_partner not in partners:
                raise ValueError("o segundo indivíduo selecionado não é parceiro registrado")
            return selected_partner
        if len(partners) == 1:
            return partners[0]
        if len(partners) > 1:
            raise ValueError("selecione também qual parceiro é o outro genitor")
        return None

    def _available_context_actions(self, item: IndividualItem) -> set[str]:
        parent_ids = {
            edge.parent_id
            for edge in self.project.parentages
            if edge.child_id == item.person.id
        }
        parents = [person for person in self.project.individuals if person.id in parent_ids]
        actions = {
            "partner", "child", "adopted_child", "sibling",
            "edit_dialog", "edit", "delete",
        }
        if len(parents) < 2:
            if not any(parent.gender_identity == GenderIdentity.MAN for parent in parents):
                actions.add("father")
            if not any(parent.gender_identity == GenderIdentity.WOMAN for parent in parents):
                actions.add("mother")
        if not parents:
            actions.add("unknown_parents")
        return actions

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
        rect = self.scene.pedigree_bounding_rect().adjusted(-80, -80, 80, 80)
        if not rect.isEmpty():
            self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self.view.zoomChanged.emit(self.view.zoom_percent)

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
        self._update_workspace_state()
        self.toast.show_message(tr("Indivíduo adicionado"))
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
        self.undo_stack.push(MoveIndividualCommand(self.scene, item, old_position, new_position))

    def _selection_changed(self) -> None:
        try:
            selected = self.scene.selected_people()
        except RuntimeError:
            return
        self.properties.set_item(selected[0] if len(selected) == 1 else None, self.project)
        if len(selected) == 1:
            self.properties_drawer.open_panel()
        else:
            self.properties_drawer.close_panel()

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
        self._update_workspace_state()
        self.statusBar().showMessage(f"Projeto salvo em {path}", 5000)
        self.toast.show_message("Projeto salvo")
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
        self._update_workspace_state()
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
            include_legend=self.settings.value("export/include_legend", True, bool),
            monochrome=self.settings.value("export/monochrome", False, bool),
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
        self.toast.show_message(tr("Exportação concluída"))

    def open_preferences(self) -> None:
        dialog = PreferencesDialog(self)
        dialog.applied.connect(self.apply_preferences)
        dialog.exec()

    def apply_preferences(self) -> None:
        font_size = self.settings.value("ui/font_size", 14, int)
        scale = self.settings.value("ui/scale", 100, int) / 100
        effective_size = max(10, round(font_size * scale))
        self.setStyleSheet(
            SCIENTIFIC_WORKSPACE_STYLESHEET + f"\n* {{ font-size: {effective_size}px; }}"
        )
        font = QFont(self.font())
        font.setPixelSize(effective_size)
        self.setFont(font)
        drawer_width = round(370 * scale)
        self.properties_drawer.setMinimumWidth(round(330 * scale))
        self.properties_drawer.setFixedWidth(drawer_width)
        self.properties_drawer.sync_geometry()
        self.tool_rail.setFixedWidth(round((210 if self.rail_expanded else 60) * scale))
        self.view.grid_enabled = self.settings.value("pedigree/grid", True, bool)
        self.scene.apply_render_style(PedigreeRenderStyle.from_settings(self.settings))
        self.view.viewport().update()
        self._update_workspace_state()

    def toggle_language(self) -> None:
        language_manager.set_language("en" if language_manager.language == "pt_BR" else "pt_BR")

    def retranslate_ui(self, _language: str | None = None) -> None:
        mapping = {
            self.new_action: "Novo",
            self.open_action: "Abrir…",
            self.save_action: "Salvar",
            self.save_as_action: "Salvar como…",
            self.quit_action: "Sair",
            self.undo_action: "Desfazer",
            self.redo_action: "Refazer",
            self.add_man_action: "Adicionar homem/menino",
            self.add_woman_action: "Adicionar mulher/menina",
            self.add_unspecified_action: "Adicionar gênero não especificado",
            self.auto_layout_action: "Organização automática",
            self.export_action: "Exportar figura…",
            self.preferences_action: "Preferências…",
            self.delete_action: "Excluir",
            self.select_action: "Selecionar",
            self.move_action: "Mover",
            self.edit_action: "Editar indivíduo",
            self.relationship_action: "Relacionamento",
            self.consanguinity_action: "Relação consanguínea",
            self.separation_action: "Relação separada",
            self.divorce_action: "Relação divorciada",
            self.add_parents_action: "Adicionar pais",
            self.add_partner_action: "Adicionar parceiro",
            self.add_child_action: "Adicionar filho",
            self.add_sibling_action: "Adicionar irmão",
            self.fit_action: "Ajustar à tela",
            self.zoom_in_action: "Ampliar",
            self.zoom_out_action: "Reduzir",
        }
        for action, source in mapping.items():
            action.setText(tr(source))
            action.setToolTip(tr(source))
        self.language_action.setText("EN" if language_manager.language == "en" else "PT")
        self.file_menu.setTitle(tr("Arquivo"))
        self.edit_menu.setTitle(tr("Editar"))
        self.pedigree_menu.setTitle(tr("Heredograma"))
        self.view_menu.setTitle(tr("Exibir"))
        self.person_button.setText(tr("Adicionar indivíduo"))
        self.family_button.setText(tr("Adicionar familiar"))
        self.empty_state.retranslate_ui()
        self.properties.retranslate_ui()
        self.properties_drawer.title.setText(tr("Propriedades do indivíduo"))
        self.scene.apply_render_style(self.scene.render_style)
        self._update_title()
        self._update_workspace_state()

    def _update_title(self) -> None:
        filename = self.current_path.name if self.current_path else tr("Sem título")
        dirty = " *" if not self.undo_stack.isClean() else ""
        self.setWindowTitle(f"{filename}{dirty} — RarePedigree Scientific Workspace")
        if hasattr(self, "project_title_label"):
            self.project_title_label.setText(filename)
            self.dirty_label.setText(tr("NÃO SALVO") if dirty else tr("SALVO"))

    def _undo_index_changed(self, _index: int) -> None:
        self._update_workspace_state()

    def _update_workspace_state(self) -> None:
        self._update_title()
        if not hasattr(self, "empty_state"):
            return
        count = len(self.project.individuals)
        self.empty_overlay.setVisible(count == 0)
        self.canvas_stack.setCurrentWidget(self.empty_overlay if count == 0 else self.view)
        if hasattr(self, "count_status"):
            unit = tr("indivíduo" if count == 1 else "indivíduos")
            self.count_status.setText(f"{count} {unit}")
        if hasattr(self, "generation_status"):
            generations = self.layout_engine.generations(self.project)
            total = len(set(generations.values())) if generations else 0
            unit = tr("geração" if total == 1 else "gerações")
            self.generation_status.setText(f"{total} {unit}")
            self.save_status.setText(
                tr("Alterado") if not self.undo_stack.isClean() else tr("Salvo")
            )

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

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if hasattr(self, "properties_drawer"):
            self.properties_drawer.sync_geometry()
