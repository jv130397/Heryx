"""Scientific figure exporters using Qt's vector/raster backends."""

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QMarginsF, QRectF, QSize
from PySide6.QtGui import QImage, QPageLayout, QPageSize, QPainter, QPdfWriter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QGraphicsScene


@dataclass(frozen=True)
class ExportOptions:
    png_scale: float = 2.0
    margin: float = 30.0
    landscape: bool = True
    include_legend: bool = True
    include_annotations: bool = False
    monochrome: bool | None = None


DEFAULT_EXPORT_OPTIONS = ExportOptions()


def _content_rect(
    scene: QGraphicsScene,
    margin: float,
    include_legend: bool = True,
    include_annotations: bool = False,
) -> QRectF:
    legend = getattr(scene, "legend_item", None)
    previous = legend.isVisible() if legend is not None else False
    if legend is not None:
        legend.setVisible(include_legend)
    notes = list(getattr(scene, "annotation_items", {}).values())
    note_visibility = [item.isVisible() for item in notes]
    for item in notes:
        item.setVisible(include_annotations and item.note.visible)
    rect = scene.itemsBoundingRect().adjusted(-margin, -margin, margin, margin)
    if legend is not None:
        legend.setVisible(previous)
    for item, visible in zip(notes, note_visibility, strict=True):
        item.setVisible(visible)
    return rect if not rect.isEmpty() else QRectF(0, 0, 640, 480)


def _render(
    scene: QGraphicsScene,
    painter: QPainter,
    target: QRectF | None,
    source: QRectF,
    options: ExportOptions,
) -> None:
    selected = scene.selectedItems()
    legend = getattr(scene, "legend_item", None)
    legend_visible = legend.isVisible() if legend is not None else False
    if legend is not None:
        legend.setVisible(options.include_legend)
    styled_items = list(getattr(scene, "person_items", {}).values())
    annotation_items = list(getattr(scene, "annotation_items", {}).values())
    annotation_visibility = [item.isVisible() for item in annotation_items]
    annotation_effects = [item.graphicsEffect() for item in annotation_items]
    for item in annotation_items:
        item.setVisible(options.include_annotations and item.note.visible)
        if item.graphicsEffect() is not None:
            item.graphicsEffect().setEnabled(False)
    original_modes = [item.render_style.monochrome for item in styled_items]
    if options.monochrome is not None:
        for item in styled_items:
            item.render_style.monochrome = options.monochrome
            item.update()
    scene.clearSelection()
    if target is None:
        scene.render(painter, source=source)
    else:
        scene.render(painter, target=target, source=source)
    for item in selected:
        item.setSelected(True)
    for item, mode in zip(styled_items, original_modes, strict=True):
        item.render_style.monochrome = mode
        item.update()
    for item, visible in zip(annotation_items, annotation_visibility, strict=True):
        item.setVisible(visible)
    for effect in annotation_effects:
        if effect is not None:
            effect.setEnabled(True)
    if legend is not None:
        legend.setVisible(legend_visible)


def export_svg(
    scene: QGraphicsScene, path: Path, options: ExportOptions = DEFAULT_EXPORT_OPTIONS
) -> None:
    rect = _content_rect(
        scene, options.margin, options.include_legend, options.include_annotations
    )
    generator = QSvgGenerator()
    generator.setFileName(str(path))
    generator.setSize(QSize(max(1, int(rect.width())), max(1, int(rect.height()))))
    generator.setViewBox(rect)
    generator.setTitle("RarePedigree Studio export")
    painter = QPainter(generator)
    _render(scene, painter, None, rect, options)
    painter.end()


def export_png(
    scene: QGraphicsScene, path: Path, options: ExportOptions = DEFAULT_EXPORT_OPTIONS
) -> None:
    rect = _content_rect(
        scene, options.margin, options.include_legend, options.include_annotations
    )
    size = QSize(
        max(1, int(rect.width() * options.png_scale)),
        max(1, int(rect.height() * options.png_scale)),
    )
    image = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill("white")
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _render(scene, painter, QRectF(0, 0, size.width(), size.height()), rect, options)
    painter.end()
    if not image.save(str(path), "PNG"):
        raise OSError(f"could not export PNG to {path}")


def export_pdf(
    scene: QGraphicsScene, path: Path, options: ExportOptions = DEFAULT_EXPORT_OPTIONS
) -> None:
    rect = _content_rect(
        scene, options.margin, options.include_legend, options.include_annotations
    )
    writer = QPdfWriter(str(path))
    writer.setTitle("RarePedigree Studio export")
    writer.setResolution(300)
    orientation = (
        QPageLayout.Orientation.Landscape if options.landscape else QPageLayout.Orientation.Portrait
    )
    writer.setPageLayout(
        QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            orientation,
            QMarginsF(10, 10, 10, 10),
        )
    )
    painter = QPainter(writer)
    _render(scene, painter, None, rect, options)
    painter.end()
