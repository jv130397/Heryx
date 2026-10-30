from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox


class PreferencesDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferências")
        self.settings = QSettings()
        self.png_scale = QSpinBox()
        self.png_scale.setRange(1, 6)
        self.png_scale.setValue(self.settings.value("export/png_scale", 2, int))
        self.margin = QSpinBox()
        self.margin.setRange(0, 200)
        self.margin.setValue(self.settings.value("export/margin", 30, int))
        self.orientation = QComboBox()
        self.orientation.addItem("Paisagem", True)
        self.orientation.addItem("Retrato", False)
        current = self.orientation.findData(
            self.settings.value("export/landscape", True, bool)
        )
        self.orientation.setCurrentIndex(max(0, current))
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QFormLayout(self)
        layout.addRow("Escala padrão do PNG", self.png_scale)
        layout.addRow("Margem da figura", self.margin)
        layout.addRow("Orientação do PDF", self.orientation)
        layout.addRow(buttons)

    def _save(self) -> None:
        self.settings.setValue("export/png_scale", self.png_scale.value())
        self.settings.setValue("export/margin", self.margin.value())
        self.settings.setValue("export/landscape", self.orientation.currentData())
        self.accept()
