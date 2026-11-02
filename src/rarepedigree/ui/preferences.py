"""Persistent, non-clinical workspace preferences."""

from PySide6.QtCore import QSettings, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.ui.clinical import HPOManagerDialog
from rarepedigree.ui.components import AccessibleCheckBox as QCheckBox
from rarepedigree.ui.i18n import language_manager, tr


class ColorButton(QPushButton):
    colorChanged = Signal(str)

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
        self.colorChanged.emit(color)

    def _refresh(self) -> None:
        self.setStyleSheet(f"border-left: 24px solid {self.color};")


class PalettePreview(QWidget):
    """Live, presentation-only preview; phenotype remains represented by fill."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.colors = ("#20262E", "#FFFFFF", "#FFFFFF")
        self.monochrome = False
        self.setMinimumHeight(86)

    def set_palette(self, colors: tuple[str, str, str], monochrome: bool) -> None:
        self.colors = colors
        self.monochrome = monochrome
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = ("#20262E", "#FFFFFF", "#FFFFFF") if self.monochrome else self.colors
        centers = [self.width() * value / 4 for value in (1, 2, 3)]
        for index, (x, color) in enumerate(zip(centers, colors, strict=True)):
            painter.setPen(QPen(QColor("#20262E"), 3))
            painter.setBrush(QColor(color))
            painter.drawEllipse(int(x - 21), 15, 42, 42)
            if index == 2:
                painter.drawText(int(x - 8), 43, "?")
            painter.drawText(int(x - 30), 77, 60, 16, 0x84, ("A", "N", "?")[index])


class PreferencesDialog(QDialog):
    applied = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Preferências…").replace("…", ""))
        self.setMinimumSize(620, 470)
        self.settings = QSettings()
        self.tabs = QTabWidget()
        self.tabs.addTab(self._appearance_tab(), tr("Aparência"))
        self.tabs.addTab(self._language_tab(), tr("Idioma"))
        self.tabs.addTab(self._pedigree_tab(), tr("Heredograma"))
        self.tabs.addTab(self._hpo_tab(), "HPO")
        self.tabs.addTab(self._export_tab(), tr("Exportação"))
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._save)
        self.buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(self.buttons)
        language_manager.languageChanged.connect(self.retranslate_ui)
        self.retranslate_ui()

    def _appearance_tab(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self.theme = QPushButton("Midnight Genomics")
        self.theme.setEnabled(False)
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
        self.monochrome = QCheckBox("Modo científico monocromático")
        self.monochrome.setChecked(self.settings.value("pedigree/monochrome", False, bool))
        self.show_legend = QCheckBox("Mostrar legenda")
        self.show_legend.setChecked(self.settings.value("pedigree/show_legend", True, bool))
        self.show_auxiliary_labels = QCheckBox("Mostrar rótulos auxiliares")
        self.show_auxiliary_labels.setChecked(
            self.settings.value("pedigree/show_auxiliary_labels", True, bool)
        )
        self.identifier_size = QSpinBox()
        self.identifier_size.setRange(8, 18)
        self.identifier_size.setValue(self.settings.value("pedigree/identifier_size", 10, int))
        self.identifier_mode = QComboBox()
        self.identifier_mode.addItem("Identificador manual", "manual")
        self.identifier_mode.addItem("Numeração genealógica (I-1, II-3)", "genealogical")
        self.identifier_mode.addItem("Numeração e identificador manual", "both")
        self.identifier_mode.setCurrentIndex(
            max(
                0,
                self.identifier_mode.findData(
                    self.settings.value("pedigree/identifier_mode", "manual", str)
                ),
            )
        )
        self.minimum_zoom = QSpinBox()
        self.minimum_zoom.setRange(1, 100)
        self.minimum_zoom.setSuffix("%")
        self.minimum_zoom.setValue(self.settings.value("navigation/minimum_zoom", 5, int))
        self.maximum_zoom = QSpinBox()
        self.maximum_zoom.setRange(100, 1000)
        self.maximum_zoom.setSuffix("%")
        self.maximum_zoom.setValue(self.settings.value("navigation/maximum_zoom", 500, int))
        self.readable_zoom = QSpinBox()
        self.readable_zoom.setRange(10, 100)
        self.readable_zoom.setSuffix("%")
        self.readable_zoom.setValue(self.settings.value("navigation/readable_zoom", 45, int))
        self.reduce_motion = QCheckBox("Reduzir movimento")
        self.reduce_motion.setChecked(self.settings.value("ui/reduce_motion", False, bool))
        self.palette = QComboBox()
        self.palette.addItem("Clássico científico", "scientific")
        self.palette.addItem("Clínico contemporâneo", "clinical")
        self.palette.addItem("Alto contraste", "contrast")
        self.palette.addItem("Acessível a daltonismo (legado)", "colorblind")
        self.affected_color = ColorButton(
            self.settings.value("phenotype/affected_color", "#20262E", str)
        )
        self.unaffected_color = ColorButton(
            self.settings.value("phenotype/unaffected_color", "#FFFFFF", str)
        )
        self.unknown_color = ColorButton(
            self.settings.value("phenotype/unknown_color", "#FFFFFF", str)
        )
        self.outline_color = ColorButton(
            self.settings.value("phenotype/outline_color", "#20262E", str)
        )
        # Compatibility alias for integrations written before the neutral
        # scientific palette. It controls phenotype fill, never sex/gender.
        self.man_color = self.affected_color
        self.outline_width = QSpinBox()
        self.outline_width.setRange(1, 6)
        self.outline_width.setValue(self.settings.value("phenotype/outline_width", 3, int))
        self.preview = PalettePreview()
        self.reset_colors = QPushButton("Restaurar cores padrão")
        self.reset_colors.clicked.connect(self._reset_colors)
        self.palette.currentIndexChanged.connect(self._apply_palette)
        for button in (
            self.affected_color,
            self.unaffected_color,
            self.unknown_color,
            self.outline_color,
        ):
            button.colorChanged.connect(self._update_preview)
        self.monochrome.toggled.connect(self._update_preview)
        self.legend_position = QComboBox()
        self.legend_position.addItem("Abaixo", "bottom")
        self.legend_position.addItem("Acima", "top")
        self.legend_position.addItem("À direita", "right")
        self.legend_position.setCurrentIndex(max(0, self.legend_position.findData(
            self.settings.value("pedigree/legend_position", "bottom", str)
        )))
        form.addRow(self.grid)
        section = QLabel("REPRESENTAÇÃO FENOTÍPICA")
        section.setProperty("sectionHeader", True)
        form.addRow(section)
        form.addRow(self.monochrome)
        form.addRow(self.show_legend)
        form.addRow(self.show_auxiliary_labels)
        form.addRow("Posição da legenda", self.legend_position)
        form.addRow("Tamanho dos identificadores", self.identifier_size)
        form.addRow("Rótulo dos indivíduos", self.identifier_mode)
        form.addRow("Zoom mínimo", self.minimum_zoom)
        form.addRow("Zoom máximo", self.maximum_zoom)
        form.addRow("Limite de legibilidade", self.readable_zoom)
        form.addRow(self.reduce_motion)
        form.addRow("Paleta", self.palette)
        form.addRow("Afetado", self.affected_color)
        form.addRow("Não afetado", self.unaffected_color)
        form.addRow("Desconhecido", self.unknown_color)
        form.addRow("Contorno neutro", self.outline_color)
        form.addRow("Espessura do contorno", self.outline_width)
        form.addRow(self.preview)
        form.addRow(self.reset_colors)
        self._update_preview()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(page)
        return scroll

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
        self.export_annotations = QCheckBox("Incluir anotações visíveis")
        self.export_annotations.setChecked(
            self.settings.value("export/include_annotations", False, bool)
        )
        form.addRow("Escala PNG", self.png_scale)
        form.addRow("Margem", self.margin)
        form.addRow("Orientação PDF", self.orientation)
        form.addRow(self.export_legend)
        form.addRow(self.export_monochrome)
        form.addRow(self.export_annotations)
        return page

    def _hpo_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        text = QLabel(
            tr(
                "A ontologia é instalada localmente e nenhuma informação clínica "
                "é enviada durante a atualização."
            )
        )
        text.setWordWrap(True)
        text.setProperty("card", True)
        manage = QPushButton(tr("Gerenciar ontologia HPO…"))
        manage.clicked.connect(lambda: HPOManagerDialog(self).exec())
        layout.addWidget(text)
        layout.addWidget(manage)
        layout.addStretch()
        return page

    def _reset_colors(self) -> None:
        self.affected_color.set_color("#20262E")
        self.unaffected_color.set_color("#FFFFFF")
        self.unknown_color.set_color("#FFFFFF")
        self.outline_color.set_color("#20262E")
        self.outline_width.setValue(3)
        self.palette.setCurrentIndex(0)

    def _apply_palette(self) -> None:
        palettes = {
            "scientific": ("#20262E", "#FFFFFF", "#FFFFFF", "#20262E"),
            "clinical": ("#A43A3A", "#FFFFFF", "#FFFFFF", "#303740"),
            "contrast": ("#000000", "#FFFFFF", "#FFFFFF", "#000000"),
            "colorblind": ("#0072B2", "#FFFFFF", "#FFFFFF", "#20262E"),
        }
        colors = palettes[self.palette.currentData()]
        for button, color in zip(
            (
                self.affected_color,
                self.unaffected_color,
                self.unknown_color,
                self.outline_color,
            ),
            colors,
            strict=True,
        ):
            button.set_color(color)

    def _update_preview(self, _value=None) -> None:
        if hasattr(self, "preview"):
            self.preview.set_palette(
                (
                    self.affected_color.color,
                    self.unaffected_color.color,
                    self.unknown_color.color,
                ),
                self.monochrome.isChecked(),
            )

    def retranslate_ui(self, _language=None) -> None:
        self.setWindowTitle(tr("Preferências…").replace("…", ""))
        for index, text in enumerate(("Aparência", "Idioma", "Heredograma", "HPO", "Exportação")):
            self.tabs.setTabText(index, tr(text))
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(tr("Salvar"))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancelar"))
        for index, text in enumerate(
            (
                "Identificador manual",
                "Numeração genealógica (I-1, II-3)",
                "Numeração e identificador manual",
            )
        ):
            self.identifier_mode.setItemText(index, tr(text))

    def _save(self) -> None:
        values = {
            "ui/font_size": self.font_size.value(),
            "ui/scale": self.ui_scale.value(),
            "pedigree/grid": self.grid.isChecked(),
            "pedigree/monochrome": self.monochrome.isChecked(),
            "pedigree/show_legend": self.show_legend.isChecked(),
            "pedigree/show_auxiliary_labels": self.show_auxiliary_labels.isChecked(),
            "pedigree/legend_position": self.legend_position.currentData(),
            "pedigree/identifier_size": self.identifier_size.value(),
            "pedigree/identifier_mode": self.identifier_mode.currentData(),
            "navigation/minimum_zoom": self.minimum_zoom.value(),
            "navigation/maximum_zoom": self.maximum_zoom.value(),
            "navigation/readable_zoom": self.readable_zoom.value(),
            "ui/reduce_motion": self.reduce_motion.isChecked(),
            "phenotype/affected_color": self.affected_color.color,
            "phenotype/unaffected_color": self.unaffected_color.color,
            "phenotype/unknown_color": self.unknown_color.color,
            "phenotype/outline_color": self.outline_color.color,
            "phenotype/outline_width": self.outline_width.value(),
            "pedigree/man_color": self.affected_color.color,
            "export/png_scale": self.png_scale.value(),
            "export/margin": self.margin.value(),
            "export/landscape": self.orientation.currentData(),
            "export/include_legend": self.export_legend.isChecked(),
            "export/monochrome": self.export_monochrome.isChecked(),
            "export/include_annotations": self.export_annotations.isChecked(),
        }
        for key, value in values.items():
            self.settings.setValue(key, value)
        language_manager.set_language(self.language.currentData())
        self.applied.emit()
        self.accept()
