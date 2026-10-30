import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QGraphicsItem, QGraphicsView

from rarepedigree.domain import GenderIdentity
from rarepedigree.ui import MainWindow


def test_add_person_supports_undo_and_redo(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    assert person in window.project.individuals
    assert person.id in window.scene.person_items
    window.undo_stack.undo()
    assert person not in window.project.individuals
    assert person.id not in window.scene.person_items
    window.undo_stack.redo()
    assert person in window.project.individuals
    assert person.id in window.scene.person_items


def test_contextual_parents_are_atomic_and_undoable(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.UNKNOWN)
    window.undo_stack.setClean()
    window._context_action(window.scene.person_items[person.id], "parents")
    assert len(window.project.individuals) == 3
    assert len(window.project.parentages) == 2
    assert len(window.scene.parentage_items) == 1
    window.undo_stack.undo()
    assert len(window.project.individuals) == 1
    window.undo_stack.redo()
    assert len(window.project.individuals) == 3


def test_contextual_delete_removes_edges_and_is_undoable(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    window._context_action(window.scene.person_items[person.id], "partner")
    assert len(window.project.relationships) == 1
    window._context_action(window.scene.person_items[person.id], "delete")
    assert person.id not in {item.id for item in window.project.individuals}
    assert window.project.relationships == []
    window.undo_stack.undo()
    assert person.id in {item.id for item in window.project.individuals}
    assert len(window.project.relationships) == 1


def test_move_mode_controls_item_mobility(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    item = window.scene.person_items[person.id]
    assert not bool(item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    window.move_action.trigger()
    assert bool(item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    assert window.view.dragMode() == QGraphicsView.DragMode.NoDrag
    window.select_action.trigger()
    assert not bool(item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable)


def test_tool_rail_collapses_and_expands(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.toggle_tool_rail()
    assert not window.rail_expanded
    assert window.tool_rail.width() == 60
    window.toggle_tool_rail()
    assert window.rail_expanded


def test_context_actions_filter_existing_parents(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    child = window.add_person(GenderIdentity.UNKNOWN)
    item = window.scene.person_items[child.id]
    assert {"father", "mother", "unknown_parents"} <= window._available_context_actions(item)
    window._context_action(item, "father")
    item = window.scene.person_items[child.id]
    actions = window._available_context_actions(item)
    assert "father" not in actions
    assert "unknown_parents" not in actions
    assert "mother" in actions


@pytest.mark.parametrize(("scale", "expected"), [(100, 330), (125, 412), (150, 495)])
def test_ui_scale_changes_workspace_geometry(qtbot, scale, expected) -> None:
    settings = QSettings()
    settings.setValue("ui/scale", scale)
    settings.setValue("ui/font_size", 14)
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.properties_dock.minimumWidth() == expected
    assert window.font().pixelSize() == round(14 * scale / 100)
    assert window.devicePixelRatioF() > 0
    settings.setValue("ui/scale", 100)
