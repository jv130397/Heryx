"""Capture real Qt Quick frames for Phase 4.8 visual evidence."""

from pathlib import Path

from PySide6.QtCore import QMetaObject, QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest

from rarepedigree.ui_next import NexusController
from rarepedigree.ui_next.app import create_engine

OUTPUT = Path("specifications/assets/phase_4_8")


def settle(app: QGuiApplication, frames: int = 8) -> None:
    for _ in range(frames):
        app.processEvents()
    QTest.qWait(220)


def save(window, name: str, app: QGuiApplication) -> None:
    settle(app)
    window.screen().grabWindow(window.winId()).save(str(OUTPUT / name))


def invoke(root: QObject, name: str, method: str = "open") -> QObject:
    target = root.findChild(QObject, name)
    invoked = target is not None and QMetaObject.invokeMethod(
        target, method, Qt.ConnectionType.DirectConnection
    )
    if not invoked:
        raise RuntimeError(f"Cannot invoke {method} on {name}")
    return target


def main() -> None:
    app = QGuiApplication.instance() or QGuiApplication([])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller = NexusController()
    controller.setLanguage("pt_BR")
    engine = create_engine(controller)
    root = engine.rootObjects()[0]
    root.setWidth(1440)
    root.setHeight(900)
    root.show()
    controller.selectPerson("")
    save(root, "01_initial_pt_br.png", app)
    controller.selectPerson(str(controller.project.individuals[-1].id))
    save(root, "02_three_generations.png", app)
    controller.selectPerson(str(controller.project.individuals[0].id))
    save(root, "03_individual_selected.png", app)
    editor = invoke(root, "personEditor")
    save(root, "04_person_editor.png", app)
    QMetaObject.invokeMethod(editor, "close", Qt.ConnectionType.DirectConnection)
    settle(app)
    menu = invoke(root, "nexusContextMenu")
    save(root, "05_context_menu.png", app)
    QMetaObject.invokeMethod(menu, "close", Qt.ConnectionType.DirectConnection)
    settle(app)
    preferences = invoke(root, "nexusPreferences")
    save(root, "06_preferences.png", app)
    QMetaObject.invokeMethod(preferences, "close", Qt.ConnectionType.DirectConnection)
    settle(app)
    controller.setLanguage("pt_BR")
    save(root, "07_workspace_pt_br.png", app)
    controller.setLanguage("en")
    save(root, "08_workspace_en.png", app)
    controller.setLanguage("pt_BR")
    root.setWidth(1366)
    root.setHeight(768)
    save(root, "09_workspace_1366x768.png", app)
    root.setWidth(1920)
    root.setHeight(1080)
    save(root, "10_workspace_1920x1080.png", app)
    root.close()


if __name__ == "__main__":
    main()
