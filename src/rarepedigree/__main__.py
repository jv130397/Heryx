"""Desktop application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from rarepedigree.ui import MainWindow
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.startup import WelcomeDialog


def main() -> int:
    """Start the local desktop editor."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("RarePedigree Studio")
    app.setOrganizationName("RarePedigree")
    language_manager.set_language(language_manager.language, emit=False)
    if (
        language_manager.is_first_run
        and WelcomeDialog().exec() != WelcomeDialog.DialogCode.Accepted
    ):
        return 0
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
