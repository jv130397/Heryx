"""Generate real Genomic Nexus screenshots and repeatable performance measurements."""

from __future__ import annotations

import json
import os
import resource
from pathlib import Path
from time import perf_counter

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import ancestor_family, apply_layout, large_family

from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "specifications" / "assets" / "phase_4_10"
OUTPUT = ROOT / "validation" / "phase_4_10"


def timed(action) -> float:
    start = perf_counter()
    action()
    return round((perf_counter() - start) * 1000, 3)


def capture(
    app: QApplication,
    project,
    name: str,
    size: tuple[int, int] = (1920, 1080),
    setup=None,
) -> str:
    window = MainWindow()
    window.resize(*size)
    window._apply_project(apply_layout(project))
    window.show()
    app.processEvents()
    window.fit_pedigree()
    if setup:
        setup(window)
    app.processEvents()
    QTest.qWait(220)
    window.minimap.raise_()
    app.processEvents()
    path = ASSETS / f"{name}.png"
    window.grab().save(str(path))
    window.undo_stack.setClean()
    window.close()
    return str(path.relative_to(ROOT))


def performance_case(app: QApplication, size: int) -> dict[str, float | int]:
    project = large_family(size)
    project.individuals[0].proband = True
    engine = PedigreeLayoutEngine()
    layout_ms = timed(lambda: engine.compute(project, preserve_locked=False))
    start = perf_counter()
    window = MainWindow()
    startup_ms = round((perf_counter() - start) * 1000, 3)
    window.resize(1366, 768)
    window.show()
    load_ms = timed(lambda: window._apply_project(apply_layout(project)))
    app.processEvents()
    fit_ms = timed(window.fit_pedigree)
    zoom_after_fit = window.view.zoom_percent
    first_id = project.individuals[0].id
    selection_ms = timed(lambda: window.navigate_to_person(first_id))
    search_ms = timed(lambda: window.search_panel.query.setText(project.individuals[-1].label))
    minimap_ms = timed(window.minimap.refresh)
    result = {
        "individuals": size,
        "startup_ms": startup_ms,
        "layout_ms": layout_ms,
        "load_ms": load_ms,
        "fit_ms": fit_ms,
        "selection_ms": selection_ms,
        "search_ms": search_ms,
        "minimap_refresh_ms": minimap_ms,
        "zoom_percent_after_fit": zoom_after_fit,
        "peak_rss_kib_process": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    window.undo_stack.setClean()
    window.close()
    return result


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    settings = QSettings()
    settings.setValue("navigation/show_minimap", True)
    settings.setValue("navigation/minimum_zoom", 5)
    settings.setValue("navigation/maximum_zoom", 500)
    app = QApplication.instance() or QApplication([])
    family = large_family(50)
    family.individuals[0].proband = True
    branches = ancestor_family(4)
    branches.individuals[0].proband = True

    evidence = {}
    evidence["workspace_empty_selection"] = capture(
        app, family, "01_workspace_no_selection"
    )
    evidence["selected_and_inspector"] = capture(
        app,
        family,
        "02_selected_inspector",
        setup=lambda window: window.navigate_to_person(window.project.individuals[0].id),
    )
    evidence["search"] = capture(
        app,
        family,
        "03_search",
        setup=lambda window: (
            window.toggle_search(),
            window.search_panel.query.setText(window.project.individuals[-1].label),
        ),
    )
    evidence["focus_proband"] = capture(
        app, family, "04_focus_proband", setup=lambda window: window.focus_on_proband(2)
    )
    evidence["maternal_branch"] = capture(
        app, branches, "05_maternal_branch", setup=lambda window: window.focus_branch("maternal")
    )
    evidence["paternal_branch"] = capture(
        app, branches, "06_paternal_branch", setup=lambda window: window.focus_branch("paternal")
    )
    evidence["minimap"] = capture(app, family, "07_live_minimap")
    evidence["overview_50"] = capture(app, family, "08_overview_50")
    evidence["focused_50"] = capture(
        app, family, "09_focused_50", setup=lambda window: window.focus_on_proband(3)
    )
    evidence["scientific"] = capture(
        app, family, "10_scientific_view", setup=lambda window: window.set_view_mode("scientific")
    )
    language_manager.set_language("pt_BR")
    evidence["pt_1366"] = capture(app, family, "11_pt_1366x768", (1366, 768))
    evidence["pt_1920"] = capture(app, family, "12_pt_1920x1080", (1920, 1080))
    language_manager.set_language("en")
    evidence["en_1366"] = capture(app, family, "13_en_1366x768", (1366, 768))
    evidence["en_1920"] = capture(app, family, "14_en_1920x1080", (1920, 1080))
    language_manager.set_language("pt_BR")
    evidence["collapsed_rail"] = capture(
        app, family, "15_collapsed_rail", setup=lambda window: window.toggle_tool_rail()
    )

    metrics = [performance_case(app, size) for size in (10, 50, 100, 200)]
    result = {
        "environment": {
            "platform": os.uname().sysname,
            "machine": os.uname().machine,
            "qt_platform": os.environ["QT_QPA_PLATFORM"],
            "measurement": (
                "perf_counter around synchronous Qt operations; peak RSS is process-wide"
            ),
        },
        "evidence": evidence,
        "performance": metrics,
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
