"""Independent entry point for the experimental Genomic Nexus interface."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QSettings, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui_next import NexusController


def create_engine(controller: NexusController | None = None) -> QQmlApplicationEngine:
    engine = QQmlApplicationEngine()
    controller = controller or NexusController(parent=engine)
    engine.setProperty("nexusController", controller)
    engine.rootContext().setContextProperty("nexus", controller)
    qml = Path(__file__).parent / "qml" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml)))
    return engine


def main() -> int:
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    QCoreApplication.setOrganizationName("RarePedigree")
    QCoreApplication.setApplicationName("RarePedigree Studio — Genomic Nexus")
    language_manager.set_language(QSettings().value("ui/language", "pt_BR", str), emit=False)
    engine = create_engine()
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
