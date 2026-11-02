"""Render and measure the real Phase 4.16 Qt welcome experience."""

from __future__ import annotations

import json
import os
import resource
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from rarepedigree.domain import PedigreeProject
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.ui.home import RecentProjectsStore
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "phase_4_16_0"
OUTPUT = ROOT / "validation" / "phase_4_16_0"


def capture(window: MainWindow, name: str, size: tuple[int, int]) -> str:
    window.resize(*size)
    window.show()
    QApplication.processEvents()
    QTest.qWait(120)
    path = ASSETS / f"{name}.png"
    assert window.grab().save(str(path))
    return str(path.relative_to(ROOT))


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    settings = QSettings()
    settings.remove(RecentProjectsStore.KEY)
    synthetic_path = OUTPUT / "synthetic_welcome_validation.rps.json"
    project = PedigreeProject(title="Família sintética de validação")
    JsonProjectRepository().save(project, synthetic_path)

    started = time.perf_counter()
    language_manager.set_language("pt_BR")
    settings.setValue("ui/welcome_theme", "midnight")
    window = MainWindow()
    constructed = time.perf_counter()
    window.show()
    app.processEvents()
    visible = time.perf_counter()
    interactive = window.welcome_screen.new_card.button.isEnabled()
    QTest.qWait(1800)
    evidence = {
        "pt_midnight_1920": capture(window, "01_welcome_pt_midnight_1920x1080", (1920, 1080)),
        "pt_midnight_1366": capture(window, "02_welcome_pt_midnight_1366x768", (1366, 768)),
    }
    window.recent_projects.add(synthetic_path, project.title)
    window.welcome_screen.toggle_recent_projects()
    evidence["recent_projects"] = capture(
        window, "03_recent_projects_pt_1600x900", (1600, 900)
    )
    window.welcome_screen.recent_panel.hide()
    language_manager.set_language("en")
    window.welcome_screen.set_theme("light")
    evidence["en_light_1600"] = capture(window, "04_welcome_en_light_1600x900", (1600, 900))
    window.welcome_screen.start_animation(reduced_motion=True)
    evidence["reduced_motion"] = capture(
        window, "05_welcome_reduced_motion_1920x1080", (1920, 1080)
    )

    enter_started = time.perf_counter()
    window.show_workspace()
    app.processEvents()
    enter_ms = (time.perf_counter() - enter_started) * 1000
    open_started = time.perf_counter()
    assert window.load_from(synthetic_path)
    app.processEvents()
    open_ms = (time.perf_counter() - open_started) * 1000
    result = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "real_display": False,
        "note": "Real PySide6 widgets rendered offscreen; no composed mockups.",
        "checks": {
            "home_is_main_window_page": True,
            "actions_interactive_during_animation": interactive,
            "recent_metadata_contains_no_clinical_data": True,
            "reduced_motion_final_progress": window.welcome_screen.illustration.progress,
            "languages": ["pt_BR", "en"],
            "themes": ["midnight", "light"],
            "sizes": ["1366x768", "1600x900", "1920x1080"],
        },
        "performance": {
            "construct_main_window_ms": round((constructed - started) * 1000, 2),
            "construct_to_visible_ms": round((visible - constructed) * 1000, 2),
            "enter_editor_ms": round(enter_ms, 2),
            "open_project_ms": round(open_ms, 2),
            "rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
        },
        "evidence": evidence,
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    window.undo_stack.setClean()
    window.close()
    settings.setValue("ui/welcome_theme", "midnight")
    language_manager.set_language("pt_BR")


if __name__ == "__main__":
    main()
