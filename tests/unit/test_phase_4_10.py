import pytest
from PySide6.QtCore import QPointF, QSettings

from rarepedigree.domain import GenderIdentity
from rarepedigree.ui import MainWindow


@pytest.fixture(autouse=True)
def _stable_navigation_preferences():
    settings = QSettings()
    defaults = {
        "navigation/minimum_zoom": 5,
        "navigation/maximum_zoom": 500,
    }
    for key, value in defaults.items():
        settings.setValue(key, value)
    yield
    for key, value in defaults.items():
        settings.setValue(key, value)


def _three_generation_window(qtbot) -> MainWindow:
    window = MainWindow()
    qtbot.addWidget(window)
    proband = window.add_person(GenderIdentity.MAN)
    proband.proband = True
    window._context_action(window.scene.person_items[proband.id], "parents")
    father = next(
        person
        for person in window.project.individuals
        if person.gender_identity == GenderIdentity.MAN and person.id != proband.id
    )
    window._context_action(window.scene.person_items[father.id], "parents")
    return window


def test_workspace_has_one_floating_zoom_bar_instead_of_minimap(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1366, 768)
    window.show()
    qtbot.wait(20)
    assert not hasattr(window, "minimap")
    assert window.zoom_control is window.floating_zoom
    assert window.floating_zoom.parent() is window.view.viewport()
    assert window.floating_zoom.geometry().right() < window.view.viewport().width()
    assert window.floating_zoom.geometry().bottom() < window.view.viewport().height()
    assert window.floating_zoom.y() > window.view.viewport().height() // 2


def test_floating_zoom_bar_controls_real_view(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.view.set_zoom(100)
    window.floating_zoom.zoomIn.emit()
    assert window.view.zoom_percent == 120
    window.floating_zoom.zoomOut.emit()
    assert window.view.zoom_percent == 100


def test_search_finds_label_and_uuid_and_navigates(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.WOMAN)
    person.label = "Index-Patient"
    window._update_workspace_state()
    window.search_panel.query.setText("index-patient")
    assert window.search_panel.results.count() == 1
    window.search_panel.advanced.setChecked(True)
    window.search_panel.query.setText(str(person.id))
    assert window.search_panel.results.count() == 1
    window.search_panel.results.itemActivated.emit(window.search_panel.results.item(0))
    assert window.scene.person_items[person.id].isSelected()
    assert not window.context_bar.isHidden()
    assert not window.properties_drawer._open


def test_focus_on_proband_uses_graph_and_dims_unrelated_people(qtbot) -> None:
    window = _three_generation_window(qtbot)
    unrelated = window.add_person(GenderIdentity.UNKNOWN)
    window.focus_on_proband(2)
    assert window.scene.person_items[unrelated.id].opacity() < 0.5
    proband = next(person for person in window.project.individuals if person.proband)
    assert window.scene.person_items[proband.id].opacity() == 1.0
    window.clear_focus()
    assert all(item.opacity() == 1.0 for item in window.scene.person_items.values())


def test_maternal_and_paternal_branches_are_distinct(qtbot) -> None:
    window = _three_generation_window(qtbot)
    proband = next(person for person in window.project.individuals if person.proband)
    parents = window.kinship_engine.parents(window.project, proband.id)
    people = {person.id: person for person in window.project.individuals}
    mother = next(
        person_id
        for person_id in parents
        if people[person_id].gender_identity == GenderIdentity.WOMAN
    )
    father = next(
        person_id
        for person_id in parents
        if people[person_id].gender_identity == GenderIdentity.MAN
    )
    window.focus_branch("maternal")
    assert window.scene.person_items[mother].opacity() == 1.0
    assert window.scene.person_items[father].opacity() < 0.5
    window.focus_branch("paternal")
    assert window.scene.person_items[father].opacity() == 1.0
    assert window.scene.person_items[mother].opacity() < 0.5


def test_scientific_view_hides_editor_chrome_and_restores_it(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    window.set_view_mode("scientific")
    assert not window.tool_rail.isVisible()
    assert not window.main_toolbar.isVisible()
    assert not window.view.grid_enabled
    assert not window.floating_zoom.isVisible()
    window.set_view_mode("overview")
    assert window.tool_rail.isVisible()
    assert window.main_toolbar.isVisible()


def test_programmatic_zoom_preserves_focal_point_and_configured_limits(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    focal = QPointF(320, 140)
    window.view.minimum_zoom = 5
    window.view.set_zoom(175, focal)
    assert window.view.zoom_percent == 175
    center = window.view.mapToScene(window.view.viewport().rect().center())
    assert abs(center.x() - focal.x()) < 5
    window.view.set_zoom(1000)
    assert window.view.zoom_percent == window.view.maximum_zoom


def test_navigation_preferences_are_applied(qtbot) -> None:
    settings = QSettings()
    settings.setValue("navigation/minimum_zoom", 8)
    settings.setValue("navigation/maximum_zoom", 420)
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.view.minimum_zoom == 8
    assert window.view.maximum_zoom == 420


def test_context_menu_exposes_only_nonredundant_person_actions(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.UNKNOWN)
    window._context_action(window.scene.person_items[person.id], "parents")
    item = window.scene.person_items[person.id]
    menu, actions = item.build_context_menu()
    del menu
    values = set(actions.values())
    assert values == {"edit_dialog", "focus", "center", "delete"}


def test_search_stays_responsive_for_two_hundred_people(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    for index in range(200):
        window.add_person(GenderIdentity.UNKNOWN).label = f"Synthetic-{index:03d}"
    window._update_workspace_state()
    window.search_panel.query.setText("Synthetic-199")
    assert window.search_panel.results.count() == 1
