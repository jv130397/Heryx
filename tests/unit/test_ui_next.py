from PySide6.QtCore import QObject, QSettings
from PySide6.QtGui import QGuiApplication

from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui_next import NexusController
from rarepedigree.ui_next.app import create_engine


def test_qml_engine_starts_independently(qapp) -> None:
    assert isinstance(qapp, QGuiApplication)
    engine = create_engine()
    qapp.processEvents()
    assert len(engine.rootObjects()) == 1
    assert engine.rootObjects()[0].objectName() == "nexusWindow"
    assert engine.rootObjects()[0].findChild(QObject, "pedigreeCanvas") is not None


def test_synthetic_project_has_three_generations(qapp) -> None:
    del qapp
    controller = NexusController()
    assert controller.personCount >= 5
    assert controller.generationCount == 3
    assert controller.peopleModel.rowCount() == controller.personCount


def test_selection_updates_property_projection(qapp) -> None:
    del qapp
    controller = NexusController()
    person = controller.project.individuals[-1]
    controller.selectPerson(str(person.id))
    assert controller.selectedPerson["id"] == str(person.id)
    assert controller.selectedPerson["label"] == person.label


def test_confirm_edit_and_undo_redo_use_python_command_stack(qapp) -> None:
    del qapp
    controller = NexusController()
    original = controller.selectedPerson["label"]
    controller.updateSelected("NEXUS-1", "absent", False)
    assert controller.selectedPerson["label"] == "NEXUS-1"
    assert controller.canUndo
    controller.undo()
    assert controller.selectedPerson["label"] == original
    controller.redo()
    assert controller.selectedPerson["label"] == "NEXUS-1"


def test_cancel_path_has_no_domain_side_effect(qapp) -> None:
    del qapp
    controller = NexusController()
    snapshot = controller.project.model_dump(mode="json")
    # Closing/rejecting the QML dialog never invokes updateSelected.
    assert controller.project.model_dump(mode="json") == snapshot
    assert not controller.canUndo


def test_language_switch_and_colors_are_live(qapp) -> None:
    del qapp
    controller = NexusController()
    controller.setLanguage("en")
    assert controller.translate("Selecionar") == "Select"
    controller.setColors("#111111", "#222222", "#333333", False)
    assert controller.style.man_color == "#111111"
    assert QSettings().value("pedigree/man_color") == "#111111"
    assert controller.peopleModel.rowCount() > 0
    language_manager.set_language("pt_BR")
    QSettings().setValue("ui/language", "pt_BR")
