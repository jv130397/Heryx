from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QMessageBox

from rarepedigree.domain import GenderIdentity
from rarepedigree.ui.dialogs import LabelConfigurationDialog
from rarepedigree.ui.main_window import MainWindow


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


def test_label_configuration_changes_only_presentation_preferences(qtbot) -> None:
    settings = QSettings()
    settings.setValue("pedigree/identifier_mode", "manual")
    dialog = LabelConfigurationDialog()
    qtbot.addWidget(dialog)
    dialog.mode.setCurrentIndex(dialog.mode.findData("both"))
    dialog._apply()
    assert settings.value("pedigree/identifier_mode") == "both"
    settings.setValue("pedigree/identifier_mode", "manual")
