"""Capture and benchmark the real native Phase 4.16 cinematic Welcome screen."""

from __future__ import annotations

import json
import os
import resource
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QSettings, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from rarepedigree.ui.home import RecentProjectsStore
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "phase_4_16_0_cinematic"
OUTPUT = ROOT / "validation" / "phase_4_16_0_cinematic"


def capture(window: MainWindow, name: str, size: tuple[int, int]) -> str:
    window.resize(*size)
    QApplication.processEvents()
    QTest.qWait(80)
    target = ASSETS / f"{name}.png"
    if not window.grab().save(str(target)):
        raise RuntimeError(f"Could not save {target}")
    return str(target.relative_to(ROOT))


def record_real_widget(window: MainWindow, seconds: float = 4.0) -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    sphere = window.welcome_screen.sphere
    window.resize(1366, 768)
    window.show()
    window.welcome_screen._clear_completed_opacity_effects()
    sphere.start()
    QApplication.processEvents()
    destination = ASSETS / "phase_4_16_0_real_interaction.mp4"
    with tempfile.TemporaryDirectory(prefix="rarepedigree-cinematic-") as temporary:
        frames = Path(temporary)
        frame_count = round(seconds * 30)
        for index in range(frame_count):
            phase = index / max(1, frame_count - 1)
            point = QPoint(
                round(sphere.width() * (0.18 + phase * 0.64)),
                round(sphere.height() * (0.42 + 0.18 * __import__("math").sin(phase * 6.28))),
            )
            QTest.mouseMove(sphere, point)
            if index == 66:
                QTest.mouseClick(sphere, Qt.MouseButton.LeftButton, pos=point)
            QTest.qWait(33)
            window.grab().save(str(frames / f"frame-{index:04d}.png"))
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-framerate",
                "30",
                "-i",
                str(frames / "frame-%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(destination),
            ],
            check=True,
        )
    return str(destination.relative_to(ROOT))


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    application = QApplication.instance() or QApplication([])
    settings = QSettings()
    settings.remove(RecentProjectsStore.KEY)
    settings.setValue("ui/reduce_motion", False)
    settings.setValue("ui/welcome_theme", "midnight")
    language_manager.set_language("pt_BR")
    started = time.perf_counter()
    window = MainWindow()
    constructed = time.perf_counter()
    window.resize(1920, 1080)
    window.show()
    application.processEvents()
    visible = time.perf_counter()
    QTest.qWait(1100)
    sphere = window.welcome_screen.sphere
    unobstructed_fps = sphere.average_fps
    evidence: dict[str, str | None] = {}
    evidence["pt_midnight_1920"] = capture(window, "01_pt_midnight_1920x1080", (1920, 1080))
    evidence["pt_midnight_1366"] = capture(window, "02_pt_midnight_1366x768", (1366, 768))
    sphere.stop()
    sphere.set_intro_progress(0.42)
    evidence["entrance"] = capture(window, "03_cinematic_entrance", (1600, 900))
    sphere.set_intro_progress(1.0)
    sphere.start()
    QTest.mouseMove(sphere, QPoint(round(sphere.width() * 0.8), round(sphere.height() * 0.3)))
    QTest.qWait(260)
    evidence["hover"] = capture(window, "04_sphere_hover_response", (1600, 900))
    QTest.mousePress(sphere, Qt.MouseButton.LeftButton, pos=QPoint(250, 250))
    QTest.mouseMove(sphere, QPoint(390, 300))
    QTest.mouseRelease(sphere, Qt.MouseButton.LeftButton, pos=QPoint(390, 300))
    QTest.qWait(120)
    evidence["drag"] = capture(window, "05_sphere_drag_inertia", (1600, 900))
    QTest.mouseClick(sphere, Qt.MouseButton.LeftButton, pos=sphere.rect().center())
    evidence["pulse"] = capture(window, "06_sphere_click_pulse", (1600, 900))
    window.welcome_screen.start_animation(reduced_motion=True)
    evidence["reduced_motion"] = capture(window, "07_reduced_motion_static", (1366, 768))
    language_manager.set_language("en")
    window.welcome_screen.set_theme("light")
    evidence["en_light"] = capture(window, "08_en_light_1920x1080", (1920, 1080))
    window.welcome_screen.set_theme("midnight")
    window.welcome_screen.start_animation(False)
    language_manager.set_language("pt_BR")
    QTest.mouseMove(window.welcome_screen.new_card, QPoint(24, 24))
    QTest.qWait(220)
    evidence["card_hover"] = capture(window, "09_card_hover_microinteraction", (1366, 768))
    evidence["video"] = record_real_widget(window)
    menu_hidden_on_welcome = not window.menuBar().isVisible()
    editor_started = time.perf_counter()
    window.show_workspace()
    application.processEvents()
    editor_ms = (time.perf_counter() - editor_started) * 1000
    evidence["editor_transition"] = capture(window, "10_editor_transition", (1366, 768))
    results = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "implementation": "Native PySide6 QWidget/QPainter; screenshots are direct widget grabs.",
        "checks": {
            "sphere_vertices": len(sphere._vertices),
            "sphere_edges": len(sphere._edges),
            "fallback_mode": sphere.fallback_mode,
            "menu_hidden_on_welcome": menu_hidden_on_welcome,
            "timer_stopped_in_editor": not sphere.timer_active,
            "themes": ["midnight", "light"],
            "languages": ["pt_BR", "en"],
            "reduced_motion": True,
        },
        "performance": {
            "construct_ms": round((constructed - started) * 1000, 2),
            "visible_ms": round((visible - constructed) * 1000, 2),
            "editor_transition_ms": round(editor_ms, 2),
            "measured_animation_fps": round(unobstructed_fps, 2),
            "rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
        },
        "evidence": evidence,
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    window.undo_stack.setClean()
    window.close()
    settings.setValue("ui/welcome_theme", "midnight")
    settings.setValue("ui/reduce_motion", False)
    language_manager.set_language("pt_BR")


if __name__ == "__main__":
    main()
