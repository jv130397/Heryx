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


DEFAULT_EXPORT_OPTIONS = ExportOptions()


def _content_rect(scene: QGraphicsScene, margin: float) -> QRectF:
    rect = scene.itemsBoundingRect().adjusted(-margin, -margin, margin, margin)
    return rect if not rect.isEmpty() else QRectF(0, 0, 640, 480)


def _render(
    scene: QGraphicsScene, painter: QPainter, target: QRectF | None, source: QRectF
) -> None:
    selected = scene.selectedItems()
    scene.clearSelection()
    if target is None:
        scene.render(painter, source=source)
    else:
        scene.render(painter, target=target, source=source)
    for item in selected:
        item.setSelected(True)


def export_svg(
    scene: QGraphicsScene, path: Path, options: ExportOptions = DEFAULT_EXPORT_OPTIONS
) -> None:
    rect = _content_rect(scene, options.margin)
    generator = QSvgGenerator()
    generator.setFileName(str(path))
    generator.setSize(QSize(max(1, int(rect.width())), max(1, int(rect.height()))))
    generator.setViewBox(rect)
    generator.setTitle("RarePedigree Studio export")
    painter = QPainter(generator)
    _render(scene, painter, None, rect)
    painter.end()


def export_png(
    scene: QGraphicsScene, path: Path, options: ExportOptions = DEFAULT_EXPORT_OPTIONS
) -> None:
    rect = _content_rect(scene, options.margin)
    size = QSize(
        max(1, int(rect.width() * options.png_scale)),
        max(1, int(rect.height() * options.png_scale)),
    )
    image = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill("white")
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _render(scene, painter, QRectF(0, 0, size.width(), size.height()), rect)
    painter.end()
    if not image.save(str(path), "PNG"):
        raise OSError(f"could not export PNG to {path}")


def export_pdf(
    scene: QGraphicsScene, path: Path, options: ExportOptions = DEFAULT_EXPORT_OPTIONS
) -> None:
    rect = _content_rect(scene, options.margin)
    writer = QPdfWriter(str(path))
    writer.setTitle("RarePedigree Studio export")
    writer.setResolution(300)
    orientation = (
        QPageLayout.Orientation.Landscape
        if options.landscape
        else QPageLayout.Orientation.Portrait
    )
    writer.setPageLayout(
        QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            orientation,
            QMarginsF(10, 10, 10, 10),
        )
    )
    painter = QPainter(writer)
    _render(scene, painter, None, rect)
    painter.end()
