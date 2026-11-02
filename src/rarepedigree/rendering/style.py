"""Presentation-only pedigree colors, separate from scientific state."""

from dataclasses import dataclass

from PySide6.QtCore import QSettings


@dataclass
class PedigreeRenderStyle:
    monochrome: bool = False
    affected_color: str = "#20262E"
    unaffected_color: str = "#FFFFFF"
    unknown_color: str = "#FFFFFF"
    outline_color: str = "#20262E"
    outline_width: int = 3
    # Legacy preference fields are retained for API/project compatibility only.
    # They no longer encode sex or affect rendering.
    man_color: str = "#20262E"
    woman_color: str = "#20262E"
    unspecified_color: str = "#20262E"
    show_legend: bool = True
    legend_position: str = "bottom"
    identifier_size: int = 10
    show_auxiliary_labels: bool = True

    def category_color(self, category: object) -> str:
        """Expose the pre-4.12 API without using it for scientific rendering."""
        value = getattr(category, "value", str(category)).lower()
        if value in {"man", "male"}:
            return self.man_color
        if value in {"woman", "female"}:
            return self.woman_color
        return self.unspecified_color

    @classmethod
    def from_settings(cls, settings: QSettings | None = None) -> "PedigreeRenderStyle":
        settings = settings or QSettings()
        return cls(
            monochrome=settings.value("pedigree/monochrome", False, bool),
            affected_color=settings.value("phenotype/affected_color", "#20262E", str),
            unaffected_color=settings.value("phenotype/unaffected_color", "#FFFFFF", str),
            unknown_color=settings.value("phenotype/unknown_color", "#FFFFFF", str),
            outline_color=settings.value("phenotype/outline_color", "#20262E", str),
            outline_width=settings.value("phenotype/outline_width", 3, int),
            show_legend=settings.value("pedigree/show_legend", True, bool),
            legend_position=settings.value("pedigree/legend_position", "bottom", str),
            identifier_size=settings.value("pedigree/identifier_size", 10, int),
            show_auxiliary_labels=settings.value("pedigree/show_auxiliary_labels", True, bool),
        )

    def phenotype_fill(self, status) -> str:
        from rarepedigree.domain import ObservationStatus

        if self.monochrome:
            return "#20262E" if status == ObservationStatus.PRESENT else "#FFFFFF"
        if status == ObservationStatus.PRESENT:
            return self.affected_color
        if status == ObservationStatus.ABSENT:
            return self.unaffected_color
        return self.unknown_color
