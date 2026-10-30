"""Desktop application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from rarepedigree.ui import MainWindow


def main() -> int:
    """Start the local desktop editor."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("RarePedigree Studio")
    app.setOrganizationName("RarePedigree")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
