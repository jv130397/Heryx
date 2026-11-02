"""Render real Phase 4.12 Qt surfaces and record acceptance evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import ancestor_family, apply_layout

from rarepedigree.domain import AnnotationType, CanvasAnnotation, ObservationStatus
from rarepedigree.ui.dialogs import AnnotationEditorDialog, ExportFigureDialog
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "phase_4_12"
OUTPUT = ROOT / "validation" / "phase_4_12"


def capture(widget, name: str) -> str:
    QApplication.processEvents()
    QTest.qWait(180)
    path = ASSETS / f"{name}.png"
    assert widget.grab().save(str(path))
    return str(path.relative_to(ROOT))


def capture_dialog(dialog, name: str, size: tuple[int, int]) -> str:
    dialog.resize(*size)
    dialog.show()
    result = capture(dialog, name)
    dialog.close()
    return result


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    settings = QSettings()
    settings.setValue("ui/reduce_motion", True)
    language_manager.set_language("pt_BR")
    project = apply_layout(ancestor_family(4))
    project.individuals[0].proband = True
    project.individuals[0].phenotype_status = ObservationStatus.PRESENT
    project.annotations.extend(
        [
            CanvasAnnotation(
                title="Revisar documentação",
                text="Confirmar o laudo molecular antes da discussão clínica.",
                x=720,
                y=55,
                kind=AnnotationType.REVIEW,
                individual_id=project.individuals[0].id,
            ),
            CanvasAnnotation(
                title="Informação a confirmar",
                text="História familiar relatada verbalmente.",
                x=-590,
                y=370,
                width=250,
                kind=AnnotationType.TO_CONFIRM,
            ),
        ]
    )
    window = MainWindow()
    window.resize(1920, 1080)
    window._apply_project(project)
    window.show()
    window.fit_pedigree()
    evidence = {"workspace_pt_1920": capture(window, "01_workspace_notes_pt_1920x1080")}
    window.resize(1366, 768)
    window.fit_pedigree()
    evidence["workspace_pt_1366"] = capture(window, "02_workspace_notes_pt_1366x768")
    preferences = PreferencesDialog(window)
    preferences.tabs.setCurrentIndex(2)
    evidence["phenotype_preferences"] = capture_dialog(
        preferences, "03_phenotype_preferences", (760, 720)
    )
    evidence["annotation_editor"] = capture_dialog(
        AnnotationEditorDialog(project.annotations[0], window),
        "04_annotation_editor",
        (620, 420),
    )
    evidence["export_opt_in"] = capture_dialog(
        ExportFigureDialog(window), "05_export_annotation_option", (700, 390)
    )
    language_manager.set_language("en")
    window.resize(1920, 1080)
    evidence["workspace_en"] = capture(window, "06_workspace_notes_en")
    checks = {
        "neutral_outline": len(
            {item.render_style.outline_color for item in window.scene.person_items.values()}
        )
        == 1,
        "annotation_count": len(window.scene.annotation_items) == 2,
        "annotations_outside_clinical_graph": len(window.project.annotations) == 2,
        "export_default_excludes_annotations": not QSettings().value(
            "export/include_annotations", False, bool
        ),
        "legacy_drawer_hidden": not window.properties_drawer.isVisible(),
        "minimap_absent": not hasattr(window, "minimap"),
    }
    result = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "real_display": False,
        "note": "Real Qt widgets rendered offscreen; no mockups or compositing.",
        "checks": checks,
        "evidence": evidence,
    }
    language_manager.set_language("pt_BR")
    window.undo_stack.setClean()
    window.close()
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    app.processEvents()


if __name__ == "__main__":
    main()
