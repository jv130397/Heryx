import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDockWidget, QGraphicsItem, QGraphicsView

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


def test_selecting_person_opens_overlay_drawer(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.add_person(GenderIdentity.MAN)
    assert not window.properties_drawer.isHidden()
    assert window.properties_drawer._open
    window.properties_drawer.close_panel()
    assert not window.properties_drawer._open


def test_new_parents_are_above_proband_without_overlap(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    proband = window.add_person(GenderIdentity.UNKNOWN)
    window._context_action(window.scene.person_items[proband.id], "parents")
    proband_item = window.scene.person_items[proband.id]
    parent_edges = [edge for edge in window.project.parentages if edge.child_id == proband.id]
    parents = [window.scene.person_items[edge.parent_id] for edge in parent_edges]
    assert len(parents) == 2
    assert all(parent.pos().y() < proband_item.pos().y() for parent in parents)
    assert parents[0].pos() != parents[1].pos()
    assert abs(parents[0].pos().x() - parents[1].pos().x()) >= 100
    assert all(parent.pos() != proband_item.pos() for parent in parents)

    window._context_action(proband_item, "partner")
    proband_item = window.scene.person_items[proband.id]
    relation = next(
        relation
        for relation in window.project.relationships
        if proband.id in {relation.member_a, relation.member_b}
    )
    partner_id = relation.member_b if relation.member_a == proband.id else relation.member_a
    partner_item = window.scene.person_items[partner_id]
    assert partner_item.pos().y() == proband_item.pos().y()
    assert partner_item.pos().x() != proband_item.pos().x()


@pytest.mark.parametrize("action", ["child", "adopted_child"])
def test_new_child_uses_single_recorded_partner_as_second_parent(qtbot, action) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    proband = window.add_person(GenderIdentity.MAN)
    window._context_action(window.scene.person_items[proband.id], "partner")
    relation = window.project.relationships[0]
    partner_id = relation.member_b if relation.member_a == proband.id else relation.member_a
    window._context_action(window.scene.person_items[proband.id], action)
    child_ids = {
        edge.child_id for edge in window.project.parentages if edge.parent_id == proband.id
    }
    assert len(child_ids) == 1
    child_id = next(iter(child_ids))
    parent_ids = {
        edge.parent_id for edge in window.project.parentages if edge.child_id == child_id
    }
    assert parent_ids == {proband.id, partner_id}


def test_two_grandparent_couples_form_separate_family_units(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    proband = window.add_person(GenderIdentity.UNKNOWN)
    window._context_action(window.scene.person_items[proband.id], "parents")
    parent_ids = [
        edge.parent_id for edge in window.project.parentages if edge.child_id == proband.id
    ]
    for parent_id in parent_ids:
        window._context_action(window.scene.person_items[parent_id], "parents")

    generations = window.layout_engine.generations(window.project)
    grandparent_relations = [
        relation
        for relation in window.project.relationships
        if generations[relation.member_a] == generations[relation.member_b] == 0
    ]
    assert len(grandparent_relations) == 2
    intervals = []
    for relation in grandparent_relations:
        x_values = sorted(
            (
                window.scene.person_items[relation.member_a].pos().x(),
                window.scene.person_items[relation.member_b].pos().x(),
            )
        )
        assert x_values[1] - x_values[0] == window.layout_engine.HORIZONTAL_SPACING
        intervals.append(x_values)
    intervals.sort()
    assert intervals[1][0] - intervals[0][1] >= window.layout_engine.FAMILY_GAP
    positions = [item.pos() for item in window.scene.person_items.values()]
    assert len({(point.x(), point.y()) for point in positions}) == len(positions)


def test_multiple_partners_require_explicit_coparent_selection(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    proband = window.add_person(GenderIdentity.MAN)
    window._context_action(window.scene.person_items[proband.id], "partner")
    window._context_action(window.scene.person_items[proband.id], "partner")
    with pytest.raises(ValueError, match="selecione também qual parceiro"):
        window._partner_for_new_child(proband.id, [])


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


@pytest.mark.parametrize(("scale", "expected"), [(100, 390), (125, 488), (150, 585)])
def test_ui_scale_changes_workspace_geometry(qtbot, scale, expected) -> None:
    settings = QSettings()
    settings.setValue("ui/scale", scale)
    settings.setValue("ui/font_size", 14)
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.properties_drawer.width() == expected
    assert window.font().pixelSize() == round(14 * scale / 100)
    assert window.devicePixelRatioF() > 0
    settings.setValue("ui/scale", 100)


def test_properties_use_only_floating_slide_over_without_dock(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1366, 768)
    window.show()
    window.add_person(GenderIdentity.MAN)
    qtbot.waitUntil(
        lambda: window.properties_drawer.geometry().right() < window.central_shell.width()
    )
    geometry = window.properties_drawer.geometry()
    assert window.findChildren(QDockWidget) == []
    assert geometry.top() == window.properties_drawer.MARGIN
    assert geometry.right() < window.central_shell.width()
    assert geometry.bottom() < window.central_shell.height()
    window.undo_stack.setClean()
    window.close()
