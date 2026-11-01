"""Capture the model-driven workspace and its real Qt overlays."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import apply_layout, large_family

from rarepedigree.ui.dialogs import AddSiblingDialog, EditIndividualDialog, NewProjectDialog
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "specifications" / "assets" / "phase_4_10_1"
OUTPUT = ROOT / "validation" / "phase_4_10_1"


def save(widget, name: str) -> str:
    QApplication.processEvents()
    QTest.qWait(220)
    path = ASSETS / f"{name}.png"
    widget.grab().save(str(path))
    return str(path.relative_to(ROOT))


def show_dialog(dialog, name: str, size: tuple[int, int] | None = None) -> str:
    if size:
        dialog.resize(*size)
    dialog.show()
    result = save(dialog, name)
    dialog.close()
    return result


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    app.processEvents()
    language_manager.set_language("pt_BR")
    project = apply_layout(large_family(50))
    project.individuals[0].proband = True
    window = MainWindow()
    window.resize(1920, 1080)
    window._apply_project(project)
    window.show()
    window.fit_pedigree()
    evidence: dict[str, str] = {}
    evidence["workspace_pt"] = save(window, "01_workspace_pt")
    window.navigate_to_person(project.individuals[0].id)
    evidence["inspector"] = save(window, "02_inspector_drawer")
    window.properties_drawer.close_panel()
    window.toggle_search()
    evidence["search_popover"] = save(window, "03_search_popover")
    window.search_panel.hide()
    menu = window.family_button.menu()
    menu.popup(window.family_button.mapToGlobal(QPoint(0, window.family_button.height())))
    evidence["family_dropdown"] = save(menu, "04_family_dropdown")
    menu.close()
    person = project.individuals[0]
    evidence["edit_modal"] = show_dialog(
        EditIndividualDialog(person, window), "05_edit_individual_modal", (640, 430)
    )
    evidence["relative_modal"] = show_dialog(
        AddSiblingDialog(person, window), "06_add_sibling_modal", (620, 390)
    )
    evidence["new_project"] = show_dialog(
        NewProjectDialog(window), "07_new_project_modal", (620, 470)
    )
    evidence["preferences"] = show_dialog(
        PreferencesDialog(window), "08_preferences", (760, 600)
    )
    language_manager.set_language("en")
    evidence["workspace_en"] = save(window, "09_workspace_en")
    language_manager.set_language("pt_BR")
    window.undo_stack.setClean()
    window.close()
    result = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "note": "Real Qt widgets rendered offscreen; no mockups or compositing.",
        "evidence": evidence,
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
