"""Capture real Phase 4.11 Qt surfaces and record structural checks."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import ancestor_family, apply_layout

from rarepedigree.ui.dialogs import ExportFigureDialog
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "phase_4_11"
OUTPUT = ROOT / "validation" / "phase_4_11"


def capture(widget, name: str) -> str:
    QApplication.processEvents()
    QTest.qWait(180)
    path = ASSETS / f"{name}.png"
    assert widget.grab().save(str(path))
    return str(path.relative_to(ROOT))


def show_dialog(dialog, name: str, size: tuple[int, int]) -> str:
    dialog.resize(*size)
    dialog.show()
    result = capture(dialog, name)
    dialog.close()
    return result


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    QSettings().setValue("accessibility/reduced_motion", True)
    language_manager.set_language("pt_BR")
    project = ancestor_family(4)
    project.individuals[0].proband = True
    window = MainWindow()
    window.resize(1920, 1080)
    window._apply_project(apply_layout(project))
    window.show()
    window.fit_pedigree()
    evidence: dict[str, str] = {}
    evidence["workspace_pt_1920"] = capture(window, "01_workspace_pt_1920x1080")
    window.resize(1366, 768)
    evidence["workspace_pt_1366"] = capture(window, "02_workspace_pt_1366x768")
    window.resize(1920, 1080)
    person = project.individuals[0]
    item = window.scene.person_items[person.id]
    item.setSelected(True)
    window._selection_changed()
    evidence["family_bar"] = capture(window, "03_contextual_family_bar")
    window._preview_contextual_action("partner")
    evidence["preview"] = capture(window, "04_relation_preview")
    window.relation_preview.clear()
    window._open_floating_editor(item)
    evidence["editor_personal"] = capture(window, "05_editor_personal")
    window.floating_editor.tabs.setCurrentIndex(1)
    evidence["editor_clinical"] = capture(window, "06_editor_clinical")
    window.floating_editor.hide()
    preferences = PreferencesDialog(window)
    preferences.tabs.setCurrentIndex(2)
    evidence["labels"] = show_dialog(
        preferences, "07_label_configuration", (800, 720)
    )
    evidence["export"] = show_dialog(
        ExportFigureDialog(window), "08_scientific_export", (700, 360)
    )
    language_manager.set_language("en")
    evidence["workspace_en"] = capture(window, "09_workspace_en")
    language_manager.set_language("pt_BR")
    checks = {
        "context_bar_over_canvas": window.context_bar.parentWidget() is window.canvas,
        "floating_editor_over_canvas": window.floating_editor.parentWidget() is window.canvas,
        "legacy_drawer_hidden_on_person_selection": not window.properties_drawer.isVisible(),
        "minimap_removed": not hasattr(window, "minimap"),
        "single_zoom_bar": window.zoom_control is window.floating_zoom,
        "zoom_bar_in_lower_half": (
            window.floating_zoom.y() > window.view.viewport().height() // 2
        ),
        "preview_is_not_domain_data": len(window.project.individuals) == len(project.individuals),
        "four_generations_rendered": len(window.scene.generation_items) == 4,
    }
    result = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "real_display": False,
        "note": "Real Qt widgets rendered offscreen; no mockups or compositing.",
        "checks": checks,
        "evidence": evidence,
    }
    window.undo_stack.setClean()
    window.close()
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    app.processEvents()


if __name__ == "__main__":
    main()
