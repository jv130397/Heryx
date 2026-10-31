from pathlib import Path

import pytest
from PySide6.QtCore import QSettings, QSize

from rarepedigree.domain import GenderIdentity
from rarepedigree.rendering.exporters import export_svg
from rarepedigree.ui import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog


def test_workspace_starts_with_functional_empty_state(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.empty_state.isVisibleTo(window.central_shell)
    window.empty_state.addRequested.emit()
    assert len(window.project.individuals) == 1
    assert not window.empty_state.isVisible()
    assert window.project_title_label.text() == "Sem título"


def test_compact_toolbar_actions_are_functional(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.add_unspecified_action.trigger()
    assert len(window.project.individuals) == 1
    window.undo_action.trigger()
    assert window.project.individuals == []
    window.redo_action.trigger()
    assert len(window.project.individuals) == 1


def test_properties_follow_selection_and_show_relations(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    window._context_action(window.scene.person_items[person.id], "partner")
    item = window.scene.person_items[person.id]
    window.scene.clearSelection()
    assert window.properties.stack.currentWidget() is window.properties.empty
    item.setSelected(True)
    assert window.properties.stack.currentWidget() is window.properties.tabs
    assert "não registrados" not in window.properties.partners_label.text()
    window.scene.clearSelection()
    assert window.properties.stack.currentWidget() is window.properties.empty


def test_parentage_connection_can_be_selected_and_inspected(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    child = window.add_person(GenderIdentity.UNKNOWN)
    window._context_action(window.scene.person_items[child.id], "parents")
    connector = window.scene.parentage_items[child.id]
    window.scene.clearSelection()
    connector.setSelected(True)
    assert "Núcleo parental" in window.properties.empty.text()
    assert "→" in window.properties.empty.text()


def test_zoom_is_bounded_and_reported(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.view.set_zoom(175)
    assert window.view.zoom_percent == 175
    assert window.zoom_control.label.text() == "175%"
    window.view.set_zoom(1000)
    assert window.view.zoom_percent == 500


@pytest.mark.parametrize(
    "size",
    [QSize(1366, 768), QSize(1600, 900), QSize(1920, 1080), QSize(2560, 1440)],
)
def test_workspace_keeps_canvas_at_supported_resolutions(qtbot, size: QSize) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(size)
    window.show()
    qtbot.wait(1)
    assert window.view.viewport().width() > size.width() * 0.45
    assert window.tool_rail.width() == 210


def test_preferences_are_persisted(qtbot) -> None:
    settings = QSettings()
    settings.remove("export")
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    dialog.png_scale.setValue(4)
    dialog.margin.setValue(44)
    dialog.orientation.setCurrentIndex(dialog.orientation.findData(False))
    dialog._save()
    restored = PreferencesDialog()
    qtbot.addWidget(restored)
    assert restored.png_scale.value() == 4
    assert restored.margin.value() == 44
    assert restored.orientation.currentData() is False


def test_export_excludes_workspace_grid_and_empty_state(qtbot, tmp_path: Path) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.add_person(GenderIdentity.UNKNOWN)
    target = tmp_path / "scientific.svg"
    export_svg(window.scene, target)
    content = target.read_text()
    assert "Comece um novo heredograma" not in content
    assert "#e5eaf0" not in content.lower()
