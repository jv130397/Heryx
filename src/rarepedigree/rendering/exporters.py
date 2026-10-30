"""Scientific figure exporters using Qt's vector/raster backends."""

from pathlib import Path

from PySide6.QtCore import QRectF, QSize
from PySide6.QtGui import QImage, QPainter, QPdfWriter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QGraphicsScene


def _content_rect(scene: QGraphicsScene) -> QRectF:
    rect = scene.itemsBoundingRect().adjusted(-30, -30, 30, 30)
    return rect if not rect.isEmpty() else QRectF(0, 0, 640, 480)


def export_svg(scene: QGraphicsScene, path: Path) -> None:
    rect = _content_rect(scene)
    generator = QSvgGenerator()
    generator.setFileName(str(path))
    generator.setSize(QSize(max(1, int(rect.width())), max(1, int(rect.height()))))
    generator.setViewBox(rect)
    generator.setTitle("RarePedigree Studio export")
    painter = QPainter(generator)
    scene.render(painter, source=rect)
    painter.end()


def export_png(scene: QGraphicsScene, path: Path, scale: float = 2.0) -> None:
    rect = _content_rect(scene)
    size = QSize(max(1, int(rect.width() * scale)), max(1, int(rect.height() * scale)))
    image = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill("white")
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    scene.render(painter, QRectF(0, 0, size.width(), size.height()), rect)
    painter.end()
    if not image.save(str(path), "PNG"):
        raise OSError(f"could not export PNG to {path}")


def export_pdf(scene: QGraphicsScene, path: Path) -> None:
    rect = _content_rect(scene)
    writer = QPdfWriter(str(path))
    writer.setTitle("RarePedigree Studio export")
    writer.setResolution(300)
    painter = QPainter(writer)
    scene.render(painter, source=rect)
    painter.end()

