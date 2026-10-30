"""Persistent, non-clinical workspace preferences."""

from PySide6.QtCore import QSettings, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.ui.i18n import language_manager, tr


class ColorButton(QPushButton):
    def __init__(self, color: str, parent=None) -> None:
        super().__init__(color.upper(), parent)
        self.color = color
        self.clicked.connect(self.choose)
        self._refresh()

    def choose(self) -> None:
        chosen = QColorDialog.getColor(QColor(self.color), self)
        if chosen.isValid():
            self.set_color(chosen.name())

    def set_color(self, color: str) -> None:
        self.color = color
        self.setText(color.upper())
        self._refresh()

    def _refresh(self) -> None:
        self.setStyleSheet(f"border-left: 24px solid {self.color};")


class PreferencesDialog(QDialog):
    applied = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Preferências…").replace("…", ""))
        self.setMinimumSize(620, 470)
        self.settings = QSettings()
        tabs = QTabWidget()
        tabs.addTab(self._appearance_tab(), tr("Aparência"))
        tabs.addTab(self._language_tab(), tr("Idioma"))
        tabs.addTab(self._pedigree_tab(), tr("Heredograma"))
        tabs.addTab(self._export_tab(), tr("Exportação"))
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(buttons)

    def _appearance_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.theme = QComboBox()
        self.theme.addItem("Midnight Genomics", "midnight")
        self.font_size = QSpinBox()
        self.font_size.setRange(12, 20)
        self.font_size.setValue(self.settings.value("ui/font_size", 14, int))
        self.ui_scale = QSpinBox()
        self.ui_scale.setRange(80, 160)
        self.ui_scale.setSuffix("%")
        self.ui_scale.setValue(self.settings.value("ui/scale", 100, int))
        form.addRow("Tema", self.theme)
        form.addRow("Tamanho da fonte", self.font_size)
        form.addRow("Escala da interface", self.ui_scale)
        return page

    def _language_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.language = QComboBox()
        self.language.addItem("Português (Brasil)", "pt_BR")
        self.language.addItem("English", "en")
        self.language.setCurrentIndex(max(0, self.language.findData(language_manager.language)))
        form.addRow(tr("Idioma"), self.language)
        return page

    def _pedigree_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.grid = QCheckBox("Mostrar grade")
        self.grid.setChecked(self.settings.value("pedigree/grid", True, bool))
        self.category_colors = QCheckBox("Colorir contornos por categoria")
        self.category_colors.setChecked(self.settings.value("pedigree/category_colors", True, bool))
        self.monochrome = QCheckBox("Modo científico monocromático")
        self.monochrome.setChecked(self.settings.value("pedigree/monochrome", False, bool))
        self.show_legend = QCheckBox("Mostrar legenda")
        self.show_legend.setChecked(self.settings.value("pedigree/show_legend", True, bool))
        self.identifier_size = QSpinBox()
        self.identifier_size.setRange(8, 18)
        self.identifier_size.setValue(self.settings.value("pedigree/identifier_size", 10, int))
        self.man_color = ColorButton(self.settings.value("pedigree/man_color", "#3B82F6", str))
        self.woman_color = ColorButton(self.settings.value("pedigree/woman_color", "#F472B6", str))
        self.unspecified_color = ColorButton(
            self.settings.value("pedigree/unspecified_color", "#94A3B8", str)
        )
        reset = QPushButton("Restaurar cores padrão")
        reset.clicked.connect(self._reset_colors)
        form.addRow(self.grid)
        form.addRow(self.category_colors)
        form.addRow(self.monochrome)
        form.addRow(self.show_legend)
        form.addRow("Tamanho dos identificadores", self.identifier_size)
        form.addRow("Masculino / quadrado", self.man_color)
        form.addRow("Feminino / círculo", self.woman_color)
        form.addRow("Não especificado / losango", self.unspecified_color)
        form.addRow(reset)
        return page

    def _export_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.png_scale = QSpinBox()
        self.png_scale.setRange(1, 6)
        self.png_scale.setValue(self.settings.value("export/png_scale", 2, int))
        self.margin = QSpinBox()
        self.margin.setRange(0, 200)
        self.margin.setValue(self.settings.value("export/margin", 30, int))
        self.orientation = QComboBox()
        self.orientation.addItem("Paisagem", True)
        self.orientation.addItem("Retrato", False)
        self.orientation.setCurrentIndex(
            max(0, self.orientation.findData(self.settings.value("export/landscape", True, bool)))
        )
        self.export_legend = QCheckBox("Incluir legenda")
        self.export_legend.setChecked(self.settings.value("export/include_legend", True, bool))
        self.export_monochrome = QCheckBox("Exportar em modo monocromático")
        self.export_monochrome.setChecked(self.settings.value("export/monochrome", False, bool))
        form.addRow("Escala PNG", self.png_scale)
        form.addRow("Margem", self.margin)
        form.addRow("Orientação PDF", self.orientation)
        form.addRow(self.export_legend)
        form.addRow(self.export_monochrome)
        return page

    def _reset_colors(self) -> None:
        self.man_color.set_color("#3B82F6")
        self.woman_color.set_color("#F472B6")
        self.unspecified_color.set_color("#94A3B8")

    def _save(self) -> None:
        values = {
            "ui/font_size": self.font_size.value(),
            "ui/scale": self.ui_scale.value(),
            "pedigree/grid": self.grid.isChecked(),
            "pedigree/category_colors": self.category_colors.isChecked(),
            "pedigree/monochrome": self.monochrome.isChecked(),
            "pedigree/show_legend": self.show_legend.isChecked(),
            "pedigree/identifier_size": self.identifier_size.value(),
            "pedigree/man_color": self.man_color.color,
            "pedigree/woman_color": self.woman_color.color,
            "pedigree/unspecified_color": self.unspecified_color.color,
            "export/png_scale": self.png_scale.value(),
            "export/margin": self.margin.value(),
            "export/landscape": self.orientation.currentData(),
            "export/include_legend": self.export_legend.isChecked(),
            "export/monochrome": self.export_monochrome.isChecked(),
        }
        for key, value in values.items():
            self.settings.setValue(key, value)
        language_manager.set_language(self.language.currentData())
        self.applied.emit()
        self.accept()
