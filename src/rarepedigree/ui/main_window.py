"""Main desktop window for the Phase 4 functional prototype."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from PySide6.QtCore import QPointF, QRectF, QSettings, QSize, Qt
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
    QMenu,
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
    KinshipEngine,
    LayoutPosition,
    ParentageKind,
    PedigreeProject,
    Relationship,
    RelationshipKind,
    SiblingKind,
    TwinZygosity,
)
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.rendering import (
    IndividualItem,
    ParentageConnectorItem,
    PedigreeScene,
    PedigreeView,
)
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
from rarepedigree.ui.dialogs import (
    AddRelativeWizard,
    AddSiblingDialog,
    EditIndividualDialog,
    EditSiblingRelationshipDialog,
    NewProjectDialog,
    ReassignBranchWizard,
)
from rarepedigree.ui.i18n import language_manager, tr
from rarepedigree.ui.icons import icon
from rarepedigree.ui.preferences import PreferencesDialog
from rarepedigree.ui.properties import PropertiesPanel
from rarepedigree.ui.theme import SCIENTIFIC_WORKSPACE_STYLESHEET
from rarepedigree.ui.workspace import IndividualSearch, PedigreeMiniMap, ViewModeControl


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
        self.kinship_engine = KinshipEngine()
        self.settings = QSettings()
        self._navigation_history: list[tuple[QPointF, int]] = []
        self.setStyleSheet(SCIENTIFIC_WORKSPACE_STYLESHEET)
        language_manager.languageChanged.connect(self.retranslate_ui)
        self._create_actions()

        self.scene = PedigreeScene()
        self.scene.on_person_moved = self._on_person_moved
        self.scene.on_context_action = self._context_action
        self.scene.context_actions = self._available_context_actions
        self.scene.on_empty_context_action = self._empty_context_action
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
        self.canvas = canvas
        self.search_panel = IndividualSearch(canvas)
        self.search_panel.hide()
        self.search_panel.personActivated.connect(self.navigate_to_person)
        self.search_panel.close_button.clicked.connect(self.search_panel.hide)
        self.minimap = PedigreeMiniMap(self.scene, self.view, canvas)
        self.minimap.navigationRequested.connect(self.view.center_smoothly)
        self.view.viewportChanged.connect(self.minimap.viewport().update)
        self.view.viewportChanged.connect(self._position_canvas_overlays)
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
        self.add_relative_action = QAction("Adicionar familiar…", self)
        self.edit_kinship_action = QAction("Editar parentesco entre selecionados…", self)
        self.reconcile_action = QAction("Identificar familiar desconhecido…", self)
        self.reassign_branch_action = QAction("Corrigir ramo de tio ou primo…", self)
        self.add_partner_action = QAction("Adicionar parceiro", self)
        self.add_child_action = QAction("Adicionar filho", self)
        self.add_sibling_action = QAction("Adicionar irmão", self)
        self.delete_action = QAction("Excluir", self, shortcut=QKeySequence.StandardKey.Delete)
        self.auto_layout_action = QAction("Organização automática", self, shortcut="Ctrl+L")
        self.fit_action = QAction("Ajustar à tela", self, shortcut="Ctrl+0")
        self.zoom_selection_action = QAction("Zoom para seleção", self, shortcut="Ctrl+2")
        self.reset_zoom_action = QAction("Restaurar 100%", self, shortcut="Ctrl+1")
        self.search_action = QAction("Buscar indivíduo…", self, shortcut="Ctrl+F")
        self.focus_proband_action = QAction("Focar no probando", self, shortcut="Ctrl+P")
        self.clear_focus_action = QAction("Limpar foco", self, shortcut="Escape")
        self.toggle_minimap_action = QAction("Mostrar minimapa", self)
        self.toggle_minimap_action.setCheckable(True)
        self.toggle_minimap_action.setChecked(True)
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
        self.add_relative_action.triggered.connect(self._open_relative_wizard)
        self.edit_kinship_action.triggered.connect(self._edit_selected_kinship)
        self.reconcile_action.triggered.connect(self._reconcile_selected_unknown)
        self.reassign_branch_action.triggered.connect(self._reassign_selected_branch)
        self.add_partner_action.triggered.connect(lambda: self._context_for_selected("partner"))
        self.add_child_action.triggered.connect(lambda: self._context_for_selected("child"))
        self.add_sibling_action.triggered.connect(lambda: self._context_for_selected("sibling"))
        self.delete_action.triggered.connect(lambda: self._context_for_selected("delete"))
        self.auto_layout_action.triggered.connect(self.auto_layout)
        self.fit_action.triggered.connect(self.fit_pedigree)
        self.zoom_selection_action.triggered.connect(self.zoom_to_selection)
        self.reset_zoom_action.triggered.connect(lambda: self.view.reset_zoom())
        self.search_action.triggered.connect(self.toggle_search)
        self.focus_proband_action.triggered.connect(self.focus_on_proband)
        self.clear_focus_action.triggered.connect(self.clear_focus)
        self.toggle_minimap_action.toggled.connect(
            lambda visible: self.minimap.setVisible(visible)
        )
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
                self.add_relative_action,
                self.edit_kinship_action,
                self.reassign_branch_action,
                self.reconcile_action,
                self.delete_action,
                self.edit_action,
                self.twins_mz_action,
                self.twins_dz_action,
            ]
        )
        self.view_menu = self.menuBar().addMenu("Exibir")
        self.view_menu.addActions([self.zoom_in_action, self.zoom_out_action])
        self.view_menu.addActions(
            [
                self.reset_zoom_action,
                self.zoom_selection_action,
                self.fit_action,
                self.auto_layout_action,
                self.search_action,
                self.focus_proband_action,
                self.clear_focus_action,
                self.toggle_minimap_action,
            ]
        )

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Ferramentas principais", self)
        self.main_toolbar = toolbar
        toolbar.setObjectName("main-toolbar")
        toolbar.setIconSize(QSize(19, 19))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        logo = QLabel()
        logo.setPixmap(icon("logo", "#38BDF8", 30).pixmap(30, 30))
        logo.setAccessibleName("RarePedigree Studio — Genomic Nexus")
        toolbar.addWidget(logo)
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
        toolbar.addSeparator()
        self.view_mode_control = ViewModeControl()
        self.view_mode_control.modeChanged.connect(self.set_view_mode)
        toolbar.addWidget(self.view_mode_control)
        self.branch_button = QToolButton()
        self.branch_button.setText("Ramos")
        self.branch_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        branch_menu = QMenu(self.branch_button)
        self.branch_actions = []
        for label, branch in (
            ("Ramo materno", "maternal"),
            ("Ramo paterno", "paternal"),
            ("Ascendentes", "ancestors"),
            ("Descendentes", "descendants"),
            ("Irmãos e meio-irmãos", "siblings"),
            ("Familiares desconhecidos", "unknown"),
        ):
            action = branch_menu.addAction(label)
            action.setData(label)
            self.branch_actions.append(action)
            action.triggered.connect(lambda _checked=False, value=branch: self.focus_branch(value))
        focus_menu = branch_menu.addMenu("Alcance do foco")
        for label, depth in (
            ("Núcleo familiar", 1),
            ("Até duas gerações", 2),
            ("Até três gerações", 3),
            ("Todos os parentes conhecidos", None),
        ):
            action = focus_menu.addAction(label)
            action.triggered.connect(
                lambda _checked=False, value=depth: self.focus_on_proband(value)
            )
        branch_menu.addSeparator()
        self.return_navigation_action = branch_menu.addAction("Retornar à visão anterior")
        self.return_navigation_action.triggered.connect(self.return_navigation)
        self.branch_button.setMenu(branch_menu)
        toolbar.addWidget(self.branch_button)
        self.addToolBar(toolbar)

    def _create_toolbox(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("tool-rail")
        panel.setFixedWidth(60)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(7, 10, 7, 10)
        layout.setSpacing(5)
        self.rail_buttons: list[QToolButton] = []
        self.rail_expanded = False
        self.collapse_action = QAction("»", self)
        self.collapse_action.triggered.connect(self.toggle_tool_rail)
        self.collapse_button = ToolRailButton(self.collapse_action, "fit", expanded=False)
        layout.addWidget(self.collapse_button)
        select_button = ToolRailButton(self.select_action, "select", expanded=False)
        self.rail_buttons.append(select_button)
        layout.addWidget(select_button)
        self.person_button = QToolButton()
        person_button = self.person_button
        person_button.setIcon(icon("person"))
        person_button.setText("Adicionar indivíduo")
        person_button.setFixedHeight(46)
        person_button.setFixedWidth(44)
        person_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
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
        family_button.setFixedWidth(44)
        family_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        family_button.setText("Adicionar familiar")
        family_button.setProperty("railButton", True)
        family_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        family_button.setMenu(
            FamilyMenu(
                [
                    self.add_relative_action,
                    self.add_parents_action,
                    self.add_partner_action,
                    self.add_child_action,
                    self.add_sibling_action,
                    self.edit_kinship_action,
                    self.reconcile_action,
                    self.reassign_branch_action,
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
            (self.focus_proband_action, "person"),
        ]:
            button = ToolRailButton(action, icon_name, expanded=False)
            self.rail_buttons.append(button)
            layout.addWidget(button)
        layout.addStretch()
        for action, icon_name in [(self.fit_action, "fit"), (self.delete_action, "delete")]:
            button = ToolRailButton(action, icon_name, expanded=False)
            self.rail_buttons.append(button)
            layout.addWidget(button)
        return panel

    def _open_relative_wizard(self) -> None:
        selected = self.scene.selected_people()
        if not selected:
            QMessageBox.information(self, tr("Família"), tr("Selecione um indivíduo."))
            return
        before = self.project.model_copy(deep=True)
        wizard = AddRelativeWizard(before, selected[0].person, self)
        if wizard.exec() != wizard.DialogCode.Accepted:
            return
        try:
            plan = wizard.result_plan()
            after = plan.apply()
        except ValueError as error:
            QMessageBox.warning(self, tr("Relação inválida"), tr(str(error)))
            return
        positions = self.layout_engine.compute(after)
        for person in after.individuals:
            person.layout.x, person.layout.y = positions[person.id]
        self.undo_stack.push(ReplaceProjectCommand(plan.label, before, after, self._apply_project))
        self.message_status.setText(tr(plan.label))
        self.toast.show_message(tr(plan.label))
        self.fit_pedigree()

    def _edit_selected_kinship(self) -> None:
        selected = self.scene.selected_people()
        if len(selected) != 2:
            QMessageBox.information(
                self, tr("Parentesco"), tr("Selecione exatamente dois indivíduos.")
            )
            return
        before = self.project.model_copy(deep=True)
        dialog = EditSiblingRelationshipDialog(before, selected[0].person, selected[1].person, self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        try:
            plan = dialog.result_plan()
            after = plan.apply()
        except ValueError as error:
            QMessageBox.warning(self, tr("Relação inválida"), tr(str(error)))
            return
        self._finish_kinship_plan(plan.label, before, after)

    def _reconcile_selected_unknown(self) -> None:
        selected = self.scene.selected_people()
        if len(selected) != 2:
            QMessageBox.information(
                self, tr("Reconciliação"), tr("Selecione um desconhecido e uma pessoa cadastrada.")
            )
            return
        unknowns = [item.person for item in selected if item.person.placeholder]
        known = [item.person for item in selected if not item.person.placeholder]
        if len(unknowns) != 1 or len(known) != 1:
            QMessageBox.warning(
                self, tr("Reconciliação"), tr("A seleção deve conter um único desconhecido.")
            )
            return
        before = self.project.model_copy(deep=True)
        try:
            plan = self.kinship_engine.reconcile_unknown(before, unknowns[0].id, known[0].id)
        except ValueError as error:
            QMessageBox.warning(self, tr("Reconciliação"), tr(str(error)))
            return
        if self.isVisible():
            answer = QMessageBox.question(
                self,
                tr("Confirmar reconciliação"),
                tr("Substituir o representante desconhecido e preservar suas relações?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self._finish_kinship_plan(plan.label, before, plan.apply())

    def _reassign_selected_branch(self) -> None:
        selected = self.scene.selected_people()
        probands = [person for person in self.project.individuals if person.proband]
        if len(selected) != 1 or len(probands) != 1:
            QMessageBox.information(
                self,
                tr("Corrigir ramo familiar"),
                tr("Selecione um tio, tia, primo ou prima e defina exatamente um probando."),
            )
            return
        relative = selected[0].person
        if self.kinship_engine.collateral_context(
            self.project, probands[0].id, relative.id
        ) is None:
            QMessageBox.warning(
                self,
                tr("Relação inválida"),
                tr("O indivíduo selecionado não é tio, tia, primo ou prima do probando."),
            )
            return
        before = self.project.model_copy(deep=True)
        wizard = ReassignBranchWizard(before, probands[0], relative, self)
        if wizard.exec() != wizard.DialogCode.Accepted:
            return
        try:
            plan = wizard.result_plan()
        except ValueError as error:
            QMessageBox.warning(self, tr("Relação inválida"), tr(str(error)))
            return
        self._finish_kinship_plan(plan.label, before, plan.apply())

    def _finish_kinship_plan(
        self, label: str, before: PedigreeProject, after: PedigreeProject
    ) -> None:
        positions = self.layout_engine.compute(after)
        for person in after.individuals:
            person.layout.x, person.layout.y = positions[person.id]
        self.undo_stack.push(ReplaceProjectCommand(label, before, after, self._apply_project))
        self.message_status.setText(tr(label))
        self.toast.show_message(tr(label))
        self.fit_pedigree()

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
            if self.rail_expanded:
                button.setMinimumWidth(0)
                button.setMaximumWidth(16777215)
            else:
                button.setFixedWidth(44)
        self.collapse_action.setText("«" if self.rail_expanded else "»")

    def _set_interaction_mode(self, mode: str) -> None:
        self.scene.set_interaction_mode(mode)
        self.view.setDragMode(
            PedigreeView.DragMode.NoDrag if mode == "move" else PedigreeView.DragMode.RubberBandDrag
        )
        cursor = Qt.CursorShape.OpenHandCursor if mode == "move" else Qt.CursorShape.ArrowCursor
        self.view.viewport().setCursor(cursor)

    def _create_statusbar(self) -> None:
        self.count_status = QLabel()
        self.generation_status = QLabel()
        self.save_status = QLabel("Salvo")
        self.validation_status = QLabel()
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
        self.statusBar().addPermanentWidget(self.validation_status)
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

    def _empty_context_action(self, action: str, position: QPointF) -> None:
        if action == "fit":
            self.fit_pedigree()
        elif action == "layout":
            self.auto_layout()
        elif action == "add":
            person = self.add_person(GenderIdentity.UNKNOWN)
            person.layout.x = position.x()
            person.layout.y = position.y()
            self.scene.person_items[person.id].setPos(position)

    def _context_action(self, item: IndividualItem, action: str) -> None:
        if action == "center":
            self.view.center_smoothly(item.scenePos())
            return
        if action == "focus":
            self.scene.clearSelection()
            item.setSelected(True)
            relevant = {item.person.id}
            relevant |= set(self.kinship_engine.ancestors(self.project, item.person.id))
            relevant |= set(self.kinship_engine.descendants(self.project, item.person.id))
            relevant |= {
                person.id
                for person in self.project.individuals
                if self.kinship_engine.sibling_kind(
                    self.project, item.person.id, person.id
                ) is not None
            }
            self._apply_focus(relevant)
            self.view_mode_control.set_mode("focused")
            return
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
                plan = self.kinship_engine.plan_child(
                    before, item.person.id, coparent_id=partner_id
                )
                after = plan.apply()
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
                kind = SiblingKind.FULL
                sibling_label = None
                if self.isVisible():
                    dialog = AddSiblingDialog(item.person, self)
                    if dialog.exec() != dialog.DialogCode.Accepted:
                        return
                    kind = dialog.sibling_kind()
                    sibling_label = dialog.sibling_label()
                plan = self.kinship_engine.plan_sibling(
                    before, item.person.id, kind, label=sibling_label
                )
                after = plan.apply()
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
            edge.parent_id for edge in self.project.parentages if edge.child_id == item.person.id
        }
        parents = [person for person in self.project.individuals if person.id in parent_ids]
        actions = {
            "partner",
            "child",
            "adopted_child",
            "sibling",
            "edit_dialog",
            "edit",
            "delete",
            "focus",
            "center",
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
            self.minimap.refresh()
            readable = self.settings.value("navigation/readable_zoom", 45, int)
            if self.view.zoom_percent < readable:
                self.toast.show_message(
                    tr("Visão geral abaixo do limite de legibilidade; use busca ou foco."),
                    "warning",
                )

    def zoom_to_selection(self) -> None:
        selected = self.scene.selectedItems()
        if not selected:
            return
        rect = QRectF()
        for item in selected:
            rect = rect.united(item.sceneBoundingRect())
        self.view.fitInView(rect.adjusted(-90, -90, 90, 90), Qt.AspectRatioMode.KeepAspectRatio)
        self.view.zoomChanged.emit(self.view.zoom_percent)
        self.view.viewportChanged.emit()

    def toggle_search(self) -> None:
        visible = not self.search_panel.isVisible()
        self.search_panel.setVisible(visible)
        if visible:
            self.search_panel.raise_()
            self.search_panel.query.setFocus()
            self.search_panel.query.selectAll()

    def navigate_to_person(self, person_id: UUID) -> None:
        item = self.scene.person_items.get(person_id)
        if item is None:
            return
        self.scene.clearSelection()
        item.setSelected(True)
        if self.view.zoom_percent < 70:
            self.view.set_zoom(75, item.scenePos())
        self.view.center_smoothly(item.scenePos())
        self.search_panel.hide()

    def _proband(self) -> Individual | None:
        return next((person for person in self.project.individuals if person.proband), None)

    def _kinship_label(self, person: Individual) -> str:
        if not hasattr(self, "_kinship_index"):
            self._kinship_index = self._build_kinship_index()
        return self._kinship_index.get(person.id, "")

    def _build_kinship_index(self) -> dict[UUID, str]:
        proband = self._proband()
        if proband is None:
            return {}
        result = {proband.id: tr("probando")}
        biological = [
            edge for edge in self.project.parentages if edge.kind == ParentageKind.BIOLOGICAL
        ]
        parents_by_child: dict[UUID, set[UUID]] = {}
        for edge in biological:
            parents_by_child.setdefault(edge.child_id, set()).add(edge.parent_id)
        parents = parents_by_child.get(proband.id, set())
        for person_id in parents:
            result[person_id] = tr("genitor")
        ancestors = self.kinship_engine.ancestors(self.project, proband.id)
        descendants = self.kinship_engine.descendants(self.project, proband.id)
        for person_id in ancestors:
            result.setdefault(person_id, tr("ascendente"))
        for person_id in descendants:
            result.setdefault(person_id, tr("descendente"))
        for person in self.project.individuals:
            if person.id in result:
                continue
            shared = parents & parents_by_child.get(person.id, set())
            if len(shared) >= 2:
                result[person.id] = tr(SiblingKind.FULL.value)
            elif shared:
                result[person.id] = tr("meio-irmão")
        for person in self.project.individuals:
            if person.id in result:
                continue
            context = self.kinship_engine.collateral_context(
                self.project, proband.id, person.id
            )
            if context is not None:
                result[person.id] = tr(context[0])
        return result

    def focus_on_proband(self, generations: int | None = 2) -> None:
        proband = self._proband()
        if proband is None:
            self.toast.show_message(tr("Defina um probando para usar o foco."), "warning")
            return
        self._remember_navigation()
        relevant = {proband.id}
        adjacency: dict[UUID, set[UUID]] = {person.id: set() for person in self.project.individuals}
        for edge in self.project.parentages:
            adjacency[edge.parent_id].add(edge.child_id)
            adjacency[edge.child_id].add(edge.parent_id)
        frontier = {proband.id}
        depth = 0
        limit = generations if generations is not None else len(self.project.individuals)
        while frontier and depth < limit:
            frontier = {near for person_id in frontier for near in adjacency[person_id]} - relevant
            relevant.update(frontier)
            depth += 1
        self._apply_focus(relevant)
        self.navigate_to_person(proband.id)
        self.view_mode_control.set_mode("focused")

    def focus_branch(self, branch: str) -> None:
        proband = self._proband()
        if proband is None:
            return
        self._remember_navigation()
        relevant = {proband.id}
        parents = self.kinship_engine.parents(self.project, proband.id, {ParentageKind.BIOLOGICAL})
        people = {person.id: person for person in self.project.individuals}
        if branch in {"maternal", "paternal"}:
            gender = GenderIdentity.WOMAN if branch == "maternal" else GenderIdentity.MAN
            roots = {
                person_id
                for person_id in parents
                if people[person_id].gender_identity == gender
            }
            relevant |= roots
            for root in roots:
                relevant |= set(self.kinship_engine.ancestors(self.project, root))
        elif branch == "ancestors":
            relevant |= set(self.kinship_engine.ancestors(self.project, proband.id))
        elif branch == "descendants":
            relevant |= set(self.kinship_engine.descendants(self.project, proband.id))
        elif branch == "siblings":
            relevant |= {
                person.id
                for person in self.project.individuals
                if self.kinship_engine.sibling_kind(self.project, proband.id, person.id) is not None
            }
        elif branch == "unknown":
            relevant |= {person.id for person in self.project.individuals if person.placeholder}
        self._apply_focus(relevant)
        bounds = QRectF()
        for person_id in relevant:
            if person_id in self.scene.person_items:
                bounds = bounds.united(self.scene.person_items[person_id].sceneBoundingRect())
        if not bounds.isEmpty():
            self.view.fitInView(
                bounds.adjusted(-100, -100, 100, 100),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            self.view.zoomChanged.emit(self.view.zoom_percent)
        self.view_mode_control.set_mode("focused")

    def _remember_navigation(self) -> None:
        center = self.view.mapToScene(self.view.viewport().rect().center())
        state = (center, self.view.zoom_percent)
        if not self._navigation_history or self._navigation_history[-1] != state:
            self._navigation_history.append(state)
        self._navigation_history = self._navigation_history[-20:]

    def return_navigation(self) -> None:
        if not self._navigation_history:
            return
        center, zoom = self._navigation_history.pop()
        self.clear_focus()
        self.view.set_zoom(zoom, center)

    def _apply_focus(self, relevant: set[UUID]) -> None:
        for person_id, item in self.scene.person_items.items():
            item.setOpacity(1.0 if person_id in relevant else 0.18)
        for item in self.scene.relationship_items.values():
            item.setOpacity(
                1.0
                if {item.relationship.member_a, item.relationship.member_b} <= relevant
                else 0.12
            )
        for item in set(self.scene.parentage_items.values()):
            represented = {edge.parent_id for edge in item.edges} | {
                edge.child_id for edge in item.edges
            }
            item.setOpacity(1.0 if represented <= relevant else 0.12)

    def clear_focus(self) -> None:
        for item in self.scene.items():
            item.setOpacity(1.0)
        if hasattr(self, "view_mode_control") and self.view_mode_control.combo.currentData() in {
            "focused",
            "scientific",
        }:
            self.view_mode_control.set_mode("overview")

    def set_view_mode(self, mode: str) -> None:
        scientific = mode == "scientific"
        self.tool_rail.setVisible(not scientific)
        self.main_toolbar.setVisible(not scientific)
        self.menuBar().setVisible(not scientific)
        self.statusBar().setVisible(not scientific)
        self.floating_zoom.setVisible(not scientific)
        self.minimap.setVisible(not scientific and self.toggle_minimap_action.isChecked())
        if scientific:
            self.toast.hide()
        self.view.grid_enabled = not scientific and self.settings.value("pedigree/grid", True, bool)
        if mode == "overview":
            self.clear_focus()
            self.fit_pedigree()
        self.view.viewport().update()

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
            connectors = [
                item
                for item in self.scene.selectedItems()
                if isinstance(item, ParentageConnectorItem)
            ]
            if len(connectors) == 1:
                self.properties.set_connection(connectors[0])
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
        drawer_width = round(390 * scale)
        self.properties_drawer.setMinimumWidth(round(330 * scale))
        self.properties_drawer.setFixedWidth(drawer_width)
        self.properties_drawer.animation.setDuration(
            0 if self.settings.value("ui/reduce_motion", False, bool) else 180
        )
        self.properties_drawer.sync_geometry()
        self.tool_rail.setFixedWidth(round((210 if self.rail_expanded else 60) * scale))
        self.view.grid_enabled = self.settings.value("pedigree/grid", True, bool)
        self.view.minimum_zoom = self.settings.value("navigation/minimum_zoom", 5, int)
        self.view.maximum_zoom = self.settings.value("navigation/maximum_zoom", 500, int)
        minimap_width = self.settings.value("navigation/minimap_width", 220, int)
        self.minimap.setFixedSize(minimap_width, round(minimap_width * 0.68))
        show_minimap = self.settings.value("navigation/show_minimap", True, bool)
        self.toggle_minimap_action.setChecked(show_minimap)
        self.minimap.setVisible(show_minimap)
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
            self.zoom_selection_action: "Zoom para seleção",
            self.reset_zoom_action: "Restaurar 100%",
            self.search_action: "Buscar indivíduo…",
            self.focus_proband_action: "Focar no probando",
            self.clear_focus_action: "Limpar foco",
            self.toggle_minimap_action: "Mostrar minimapa",
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
        self.branch_button.setText(tr("Ramos"))
        for action in self.branch_actions:
            action.setText(tr(action.data()))
        self.search_panel.retranslate_ui()
        self.view_mode_control.retranslate_ui()
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
        if hasattr(self, "_kinship_index"):
            del self._kinship_index
        self.search_panel.set_project(self.project, self._kinship_label)
        self.minimap.refresh()
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
            issues = self.kinship_engine.validator.validate(self.project)
            errors = [issue for issue in issues if issue.severity.value == "error"]
            self.validation_status.setText(
                tr("Validação: sem erros")
                if not errors
                else tr("Validação: erros") + f" ({len(errors)})"
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
        self._position_canvas_overlays()

    def _position_canvas_overlays(self) -> None:
        if hasattr(self, "minimap"):
            self.minimap.move(
                max(18, self.canvas.width() - self.minimap.width() - 18),
                max(18, self.canvas.height() - self.minimap.height() - 18),
            )
            self.minimap.raise_()
        if hasattr(self, "search_panel"):
            width = min(460, max(320, self.canvas.width() - 48))
            self.search_panel.setFixedWidth(width)
            self.search_panel.move(max(24, (self.canvas.width() - width) // 2), 18)
