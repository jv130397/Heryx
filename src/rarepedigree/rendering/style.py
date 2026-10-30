"""Presentation-only pedigree colors, separate from scientific state."""

from dataclasses import dataclass

from PySide6.QtCore import QSettings

from rarepedigree.domain import GenderIdentity


@dataclass
class PedigreeRenderStyle:
    category_colors: bool = True
    monochrome: bool = False
    man_color: str = "#3B82F6"
    woman_color: str = "#F472B6"
    unspecified_color: str = "#94A3B8"
    show_legend: bool = True
    legend_position: str = "bottom"
    identifier_size: int = 10

    @classmethod
    def from_settings(cls, settings: QSettings | None = None) -> "PedigreeRenderStyle":
        settings = settings or QSettings()
        return cls(
            category_colors=settings.value("pedigree/category_colors", True, bool),
            monochrome=settings.value("pedigree/monochrome", False, bool),
            man_color=settings.value("pedigree/man_color", "#3B82F6", str),
            woman_color=settings.value("pedigree/woman_color", "#F472B6", str),
            unspecified_color=settings.value("pedigree/unspecified_color", "#94A3B8", str),
            show_legend=settings.value("pedigree/show_legend", True, bool),
            legend_position=settings.value("pedigree/legend_position", "bottom", str),
            identifier_size=settings.value("pedigree/identifier_size", 10, int),
        )

    def category_color(self, gender: GenderIdentity) -> str:
        if self.monochrome or not self.category_colors:
            return "#20262E"
        if gender == GenderIdentity.MAN:
            return self.man_color
        if gender == GenderIdentity.WOMAN:
            return self.woman_color
        return self.unspecified_color
