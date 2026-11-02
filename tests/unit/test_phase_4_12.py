from pathlib import Path

from PySide6.QtCore import QPointF, QSettings

from rarepedigree.domain import (
    AnnotationType,
    CanvasAnnotation,
    GenderIdentity,
    Individual,
    ObservationStatus,
    PedigreeProject,
)
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.rendering import PedigreeScene
from rarepedigree.rendering.exporters import ExportOptions, export_svg
from rarepedigree.rendering.style import PedigreeRenderStyle
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog


def test_geometry_not_color_encodes_gender() -> None:
    style = PedigreeRenderStyle(man_color="#123456", woman_color="#ABCDEF")
    assert style.outline_color == "#20262E"
    assert style.phenotype_fill(ObservationStatus.PRESENT) == "#20262E"
    assert style.phenotype_fill(ObservationStatus.ABSENT) == "#FFFFFF"


def test_monochrome_preserves_unknown_marker_semantics() -> None:
    style = PedigreeRenderStyle(monochrome=True, affected_color="#A43A3A")
    assert style.phenotype_fill(ObservationStatus.PRESENT) == "#20262E"
    assert style.phenotype_fill(ObservationStatus.UNKNOWN) == "#FFFFFF"


def test_phase_4_12_palette_updates_live_preview(qtbot) -> None:
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    dialog.palette.setCurrentIndex(dialog.palette.findData("clinical"))
    assert dialog.affected_color.color == "#A43A3A"
    assert dialog.preview.colors[0] == "#A43A3A"


def test_annotation_create_undo_redo_and_shortcut(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._add_annotation(QPointF(120, 180))
    assert len(window.project.annotations) == 1
    assert window.add_annotation_action.shortcut().toString() == "Ctrl+Shift+N"
    window.undo_stack.undo()
    assert not window.project.annotations
    window.undo_stack.redo()
    assert window.project.annotations[0].x == 120


def test_annotation_move_is_undoable(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window._add_annotation(QPointF(10, 20))
    note = window.project.annotations[0]
    item = window.scene.annotation_items[note.id]
    item.setPos(90, 110)
    item.note.x, item.note.y = 90, 110
    window._annotation_action(item, "geometry", (10, 20, note.width, note.height))
    assert window.project.annotations[0].x == 90
    window.undo_stack.undo()
    assert window.project.annotations[0].x == 10


def test_annotations_round_trip_without_becoming_clinical_data(tmp_path: Path) -> None:
    person = Individual(label="I-1", gender_identity=GenderIdentity.MAN)
    note = CanvasAnnotation(
        title="Revisar",
        text="Confirmar com a família",
        kind=AnnotationType.REVIEW,
        individual_id=person.id,
    )
    project = PedigreeProject(individuals=[person], annotations=[note])
    path = tmp_path / "notes.rps.json"
    repository = JsonProjectRepository()
    repository.save(project, path)
    loaded = repository.load(path)
    assert loaded.annotations[0].individual_id == person.id
    assert loaded.annotations[0].kind == AnnotationType.REVIEW
    assert loaded.individuals[0].phenotype_status == ObservationStatus.UNKNOWN


def test_annotation_export_is_opt_in(qapp, tmp_path: Path) -> None:
    del qapp
    note = CanvasAnnotation(title="NOTA_VISUAL", text="Somente comentário", x=400, y=300)
    scene = PedigreeScene()
    scene.load_project(PedigreeProject(annotations=[note]))
    hidden = tmp_path / "hidden.svg"
    visible = tmp_path / "visible.svg"
    export_svg(scene, hidden, ExportOptions(include_annotations=False))
    export_svg(scene, visible, ExportOptions(include_annotations=True))
    assert hidden.read_bytes() != visible.read_bytes()
    assert b"NOTA_VISUAL" not in hidden.read_bytes()
    assert b"NOTA_VISUAL" in visible.read_bytes()


def test_legacy_category_preferences_do_not_change_neutral_outline() -> None:
    settings = QSettings()
    settings.setValue("pedigree/man_color", "#0000FF")
    settings.setValue("pedigree/woman_color", "#FF00FF")
    assert PedigreeRenderStyle.from_settings(settings).outline_color == settings.value(
        "phenotype/outline_color", "#20262E", str
    )
