"""First-run language onboarding."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QPushButton, QVBoxLayout

from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.theme import SCIENTIFIC_WORKSPACE_STYLESHEET


class WelcomeDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet(SCIENTIFIC_WORKSPACE_STYLESHEET)
        self.setObjectName("welcome-dialog")
        self.setWindowTitle("Welcome to RarePedigree Studio")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(16)
        mark = QLabel("⬡")
        mark.setObjectName("welcome-mark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("Welcome to RarePedigree Studio")
        title.setObjectName("welcome-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt = QLabel("Choose your preferred language / Escolha seu idioma")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.language_combo = QComboBox()
        self.language_combo.addItem("Português (Brasil)", "pt_BR")
        self.language_combo.addItem("English", "en")
        button = QPushButton("Continue / Continuar")
        button.setObjectName("primary-button")
        button.clicked.connect(self.accept_language)
        layout.addWidget(mark)
        layout.addWidget(title)
        layout.addWidget(prompt)
        layout.addWidget(self.language_combo)
        layout.addWidget(button)

    def accept_language(self) -> None:
        language_manager.set_language(self.language_combo.currentData())
        language_manager.complete_first_run()
        self.accept()
