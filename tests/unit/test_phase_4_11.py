from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QMessageBox, QPushButton

from rarepedigree.domain import GenderIdentity
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog


def test_selection_opens_context_points_and_escape_closes(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.add_person(GenderIdentity.MAN)
    assert not window.context_bar.isHidden()
    visible_points = [
        button
        for button in window.context_bar._buttons.values()
        if not button.isHidden()
    ]
    assert len(visible_points) >= 3
    qtbot.keyClick(window.context_bar, Qt.Key.Key_Escape)
    assert window.context_bar.isHidden()


def test_context_preview_is_disposable_and_cancel_does_not_mutate(qtbot, monkeypatch) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.add_person(GenderIdentity.MAN)
    before = window.project.model_dump(mode="json")
    window._preview_contextual_action("partner")
    assert window.relation_preview.group is not None
    window.relation_preview.clear()
    assert window.relation_preview.group is None
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )
    window._request_contextual_action("partner")
    assert window.project.model_dump(mode="json") == before


def test_confirmed_context_parent_addition_is_undoable(qtbot, monkeypatch) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.add_person(GenderIdentity.MAN)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window._request_contextual_action("parents")
    assert len(window.project.individuals) == 3
    assert len(window.project.parentages) == 2
    window.undo_stack.undo()
    assert len(window.project.individuals) == 1
    assert not window.project.parentages


def test_floating_editor_updates_clinical_state_and_undo(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    item = window.scene.person_items[person.id]
    window._open_floating_editor(item)
    assert not window.floating_editor.isHidden()
    window.floating_editor.label_edit.setText("III-2 manual")
    window.floating_editor.phenotype.setCurrentIndex(1)
    window.floating_editor._save()
    assert item.person.label == "III-2 manual"
    assert item.person.phenotype_status.value == "present"
    window.undo_stack.undo()
    assert item.person.label != "III-2 manual"


def test_context_surfaces_remain_inside_canvas_after_navigation(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1366, 768)
    window.show()
    window.add_person(GenderIdentity.WOMAN)
    window.view.set_zoom(175)
    window._position_context_surfaces()
    geometry = window.context_bar.geometry()
    assert geometry.left() >= 0
    assert geometry.top() >= 0
    assert geometry.right() <= window.canvas.width()
    assert geometry.bottom() <= window.canvas.height()
    window.undo_stack.setClean()
    window.close()


def test_label_configuration_uses_single_preferences_source(qtbot, monkeypatch) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    opened_tabs: list[int] = []

    def record_tab(dialog) -> int:
        opened_tabs.append(dialog.tabs.currentIndex())
        return 0

    monkeypatch.setattr(PreferencesDialog, "exec", record_tab)
    window.open_label_configuration()
    assert opened_tabs == [2]


def test_relationship_inspector_contains_no_editing_controls(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.properties.findChildren(QLineEdit) == []
    assert window.properties.findChildren(QPushButton) == []
    assert not hasattr(window, "properties_dock")


def test_family_creation_exists_only_on_selected_person(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert not hasattr(window, "family_button")
    assert not hasattr(window, "person_button")
    menu_labels = {action.text() for action in window.pedigree_menu.actions()}
    assert "Adicionar pais" not in menu_labels
    assert "Adicionar parceiro" not in menu_labels
    assert "Adicionar filho" not in menu_labels
    assert "Adicionar irmão" not in menu_labels
    window.add_person(GenderIdentity.UNKNOWN)
    assert not window.context_bar.isHidden()
    assert {"parents", "partner", "child", "sibling"} <= {
        key for key, button in window.context_bar._buttons.items() if not button.isHidden()
    }


def test_visible_new_person_uses_entry_animation(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.settings.setValue("ui/reduce_motion", False)
    window.show()
    person = window.add_person(GenderIdentity.UNKNOWN)
    assert person.id in window.scene._entry_animations
    qtbot.waitUntil(lambda: person.id not in window.scene._entry_animations, timeout=1000)
    item = window.scene.person_items[person.id]
    assert item.opacity() == 1.0
    assert item.scale() == 1.0
    window._context_action(item, "parents")
    window.undo_stack.setClean()
    relative_ids = {entry.id for entry in window.project.individuals} - {person.id}
    assert relative_ids <= set(window.scene._entry_animations)
    qtbot.waitUntil(
        lambda: not relative_ids.intersection(window.scene._entry_animations), timeout=1000
    )
    window.close()
