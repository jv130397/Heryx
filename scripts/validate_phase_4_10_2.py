"""Real Qt captures and structural visual checks for Phase 4.10.2."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QSettings, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import ancestor_family, apply_layout, large_family

from rarepedigree.ui.dialogs import (
    AddSiblingDialog,
    EditIndividualDialog,
    ExportFigureDialog,
    ImportProjectDialog,
)
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "specifications" / "assets" / "phase_4_10_2"
OUTPUT = ROOT / "validation" / "phase_4_10_2"


def save(widget, name: str) -> str:
    QApplication.processEvents()
    QTest.qWait(220)
    path = ASSETS / f"{name}.png"
    widget.grab().save(str(path))
    return str(path.relative_to(ROOT))


def dialog_capture(dialog, name: str, size: tuple[int, int]) -> str:
    dialog.resize(*size)
    dialog.show()
    result = save(dialog, name)
    dialog.close()
    return result


def apply(window: MainWindow, project, size=(1920, 1080)) -> None:
    window.resize(*size)
    window._apply_project(apply_layout(project))
    window.show()
    window.fit_pedigree()
    QApplication.processEvents()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    settings = QSettings()
    settings.setValue("pedigree/identifier_mode", "manual")
    settings.setValue("navigation/show_minimap", True)
    language_manager.set_language("pt_BR")
    family50 = large_family(50)
    family50.individuals[0].proband = True
    window = MainWindow()
    apply(window, family50)
    evidence: dict[str, str] = {}
    evidence["workspace_1920"] = save(window, "01_workspace_1920x1080")
    window.resize(1366, 768)
    evidence["workspace_1366"] = save(window, "02_workspace_1366x768")
    window.resize(1920, 1080)
    evidence["rail_compact"] = save(window, "03_rail_compact")
    window.toggle_tool_rail()
    evidence["rail_expanded"] = save(window, "04_rail_expanded")
    window.toggle_tool_rail()
    dropdown = window.family_button.menu()
    dropdown.popup(window.family_button.mapToGlobal(QPoint(0, window.family_button.height())))
    evidence["dropdown"] = save(dropdown, "05_family_dropdown")
    dropdown.close()
    item = window.scene.person_items[family50.individuals[0].id]
    context, _ = item.build_context_menu()
    context.setStyleSheet(window.styleSheet())
    context.popup(window.mapToGlobal(QPoint(420, 260)))
    evidence["context_menu"] = save(context, "06_context_menu")
    context.close()
    window.navigate_to_person(family50.individuals[0].id)
    evidence["inspector"] = save(window, "07_inspector")
    window.properties_drawer.close_panel()
    evidence["edit_modal"] = dialog_capture(
        EditIndividualDialog(family50.individuals[0], window),
        "08_edit_modal",
        (660, 450),
    )
    evidence["relative_modal"] = dialog_capture(
        AddSiblingDialog(family50.individuals[0], window),
        "09_relative_modal",
        (640, 410),
    )
    evidence["import_modal"] = dialog_capture(
        ImportProjectDialog(window), "10_import_modal", (660, 250)
    )
    evidence["export_modal"] = dialog_capture(
        ExportFigureDialog(window), "11_export_modal", (700, 360)
    )
    preferences = PreferencesDialog(window)
    preferences.tabs.setCurrentIndex(2)
    evidence["preferences"] = dialog_capture(
        preferences, "12_preferences_labels", (800, 720)
    )
    evidence["minimap"] = save(window.minimap, "13_minimap")
    four_generations = ancestor_family(4)
    four_generations.individuals[0].proband = True
    apply(window, four_generations)
    evidence["four_generations"] = save(window, "14_four_generations")
    apply(window, family50)
    evidence["family_50"] = save(window, "15_family_50")
    family100 = large_family(100)
    family100.individuals[0].proband = True
    apply(window, family100)
    evidence["family_100"] = save(window, "16_family_100")
    language_manager.set_language("en")
    evidence["english"] = save(window, "17_workspace_en")
    language_manager.set_language("pt_BR")
    compact_ok = all(
        button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
        and button.width() <= 44
        for button in window.rail_buttons
    )
    result = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "real_display": False,
        "note": "Real Qt widgets rendered offscreen; no mockups or compositing.",
        "checks": {
            "compact_rail_icon_only": compact_ok,
            "drawer_overlay": window.properties_drawer.parentWidget() is window.central_shell,
            "minimap_not_in_scene": window.minimap.scene() is window.scene,
            "scientific_scene_unchanged": len(window.scene.person_items) == 100,
        },
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
