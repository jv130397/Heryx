"""Capture the real editorial Welcome screen in its supported states."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "phase_4_16_editorial"
OUTPUT = ROOT / "validation" / "phase_4_16_editorial"


def capture(window: MainWindow, name: str, size: tuple[int, int]) -> str:
    window.resize(*size)
    window.welcome_screen._clear_completed_opacity_effects()
    QApplication.processEvents()
    QTest.qWait(80)
    path = ASSETS / f"{name}.png"
    if not window.grab().save(str(path)):
        raise RuntimeError(f"Could not save {path}")
    return str(path.relative_to(ROOT))


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    settings = QSettings()
    settings.setValue("ui/welcome_theme", "midnight")
    settings.setValue("ui/reduce_motion", False)
    language_manager.set_language("pt_BR")
    window = MainWindow()
    window.show()
    app.processEvents()
    QTest.qWait(2100)
    evidence = {
        "pt_1920": capture(window, "01_editorial_pt_1920x1080", (1920, 1080)),
        "pt_1366": capture(window, "02_editorial_pt_1366x768", (1366, 768)),
    }
    pedigree = window.welcome_screen.illustration
    QTest.mouseMove(pedigree, pedigree._point(pedigree.people[7]).toPoint())
    QTest.qWait(100)
    evidence["clinical_hover"] = capture(window, "03_clinical_hover", (1366, 768))
    window.welcome_screen.start_animation(reduced_motion=True)
    evidence["reduced_motion"] = capture(window, "04_reduced_motion", (1366, 768))
    language_manager.set_language("en")
    window.welcome_screen.set_theme("light")
    evidence["en_light"] = capture(window, "05_editorial_en_light", (1920, 1080))
    result = {
        "implementation": "Native PySide6/QPainter living pedigree",
        "checks": {
            "people": len(pedigree.people),
            "proband_count": sum(person.proband for person in pedigree.people),
            "menu_hidden": not window.menuBar().isVisible(),
            "recent_action_secondary": window.welcome_screen.recent_card.property(
                "secondaryAction"
            ),
            "reduced_motion_timer_stopped": not pedigree.timer_active,
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
    settings.setValue("ui/reduce_motion", False)
    language_manager.set_language("pt_BR")


if __name__ == "__main__":
    main()
