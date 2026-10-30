from pathlib import Path

from PySide6.QtCore import QSettings

from rarepedigree.domain import GenderIdentity, Individual, ObservationStatus
from rarepedigree.rendering import PedigreeRenderStyle, PedigreeScene
from rarepedigree.rendering.exporters import ExportOptions, export_svg
from rarepedigree.ui.dialogs import EditIndividualDialog, NewProjectDialog
from rarepedigree.ui.i18n import language_manager, tr
from rarepedigree.ui.preferences import PreferencesDialog
from rarepedigree.ui.startup import WelcomeDialog


def test_first_run_language_selection_is_persisted(qtbot) -> None:
    settings = QSettings()
    settings.remove("ui/language_selected")
    dialog = WelcomeDialog()
    qtbot.addWidget(dialog)
    dialog.language_combo.setCurrentIndex(dialog.language_combo.findData("en"))
    dialog.accept_language()
    assert settings.value("ui/language_selected", False, bool)
    assert settings.value("ui/language") == "en"


def test_language_can_change_without_restart(qapp) -> None:
    del qapp
    language_manager.set_language("en")
    assert tr("Salvar") == "Save"
    language_manager.set_language("pt_BR")
    assert tr("Salvar") == "Salvar"


def test_render_colors_do_not_replace_phenotype_state(qapp) -> None:
    del qapp
    person = Individual(
        gender_identity=GenderIdentity.WOMAN,
        phenotype_status=ObservationStatus.PRESENT,
    )
    scene = PedigreeScene()
    scene.render_style = PedigreeRenderStyle(woman_color="#123456")
    scene.load_project(scene.project.model_copy(update={"individuals": [person]}))
    item = scene.person_items[person.id]
    assert item.render_style.category_color(person.gender_identity) == "#123456"
    assert item.person.phenotype_status == ObservationStatus.PRESENT


def test_monochrome_export_restores_interactive_colors(qapp, tmp_path: Path) -> None:
    del qapp
    person = Individual(gender_identity=GenderIdentity.MAN)
    scene = PedigreeScene()
    scene.render_style = PedigreeRenderStyle(man_color="#3B82F6")
    scene.load_project(scene.project.model_copy(update={"individuals": [person]}))
    target = tmp_path / "mono.svg"
    export_svg(scene, target, ExportOptions(monochrome=True))
    assert target.exists()
    assert scene.person_items[person.id].render_style.monochrome is False


def test_edit_dialog_cancel_does_not_touch_person(qtbot) -> None:
    person = Individual(label="Original")
    dialog = EditIndividualDialog(person)
    qtbot.addWidget(dialog)
    dialog.label_edit.setText("Alterado")
    dialog.reject()
    assert person.label == "Original"


def test_edit_dialog_produces_validated_values(qtbot) -> None:
    person = Individual(label="I-1")
    dialog = EditIndividualDialog(person)
    qtbot.addWidget(dialog)
    dialog.label_edit.setText("II-2")
    dialog.proband.setChecked(True)
    values = dialog.values()
    assert values["label"] == "II-2"
    assert values["proband"] is True


def test_new_project_assistant_creates_only_synthetic_metadata(qtbot) -> None:
    dialog = NewProjectDialog()
    qtbot.addWidget(dialog)
    dialog.name.setText("Família sintética")
    dialog.family_id.setText("SYN-001")
    dialog.synthetic.setChecked(True)
    project = dialog.create_project()
    assert project.title == "Família sintética"
    assert project.family.label == "SYN-001"
    assert len(project.individuals) == 5
    assert all("patient" not in person.label.lower() for person in project.individuals)


def test_preferences_persist_colors_and_legend(qtbot) -> None:
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    dialog.man_color.set_color("#112233")
    dialog.show_legend.setChecked(False)
    dialog._save()
    settings = QSettings()
    assert settings.value("pedigree/man_color") == "#112233"
    assert settings.value("pedigree/show_legend", True, bool) is False


def test_preferences_palette_preview_and_legend_position(qtbot) -> None:
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    dialog.palette.setCurrentIndex(dialog.palette.findData("colorblind"))
    dialog.legend_position.setCurrentIndex(dialog.legend_position.findData("right"))
    assert dialog.man_color.color == "#0072B2"
    assert dialog.preview.colors[0] == "#0072B2"
    dialog._save()
    assert QSettings().value("pedigree/legend_position") == "right"


def test_open_preferences_dialog_retranslates_without_restart(qtbot) -> None:
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    language_manager.set_language("en")
    assert dialog.tabs.tabText(0) == "Appearance"
    assert dialog.buttons.button(dialog.buttons.StandardButton.Save).text() == "Save"
    language_manager.set_language("pt_BR")
