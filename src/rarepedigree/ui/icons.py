# ruff: noqa: E501
"""Small dependency-free SVG icon set for the desktop workspace."""

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PATHS = {
    "new": "M12 5v14M5 12h14",
    "open": "M3 7h7l2 2h9l-2 10H5z",
    "save": "M5 4h12l2 2v14H5z M8 4v6h8V4 M8 16h8",
    "undo": "M9 7l-5 5 5 5 M5 12h8a6 6 0 0 1 6 6",
    "redo": "M15 7l5 5-5 5 M19 12h-8a6 6 0 0 0-6 6",
    "layout": "M4 4h6v6H4z M14 4h6v6h-6z M9 16h6v5H9z M7 10v3h10v-3 M12 13v3",
    "export": "M12 3v12 M7 8l5-5 5 5 M5 14v6h14v-6",
    "settings": "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 3v2 M12 19v2 M3 12h2 M19 12h2 M5.6 5.6 7 7 M17 17l1.4 1.4 M18.4 5.6 17 7 M7 17l-1.4 1.4",
    "select": "M5 3l13 9-6 1 3 6-2 1-3-6-5 4z",
    "person": "M12 4a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M5 21c0-5 3-7 7-7s7 2 7 7",
    "family": "M8 5a3 3 0 1 0 0 6 3 3 0 0 0 0-6 M16 5a3 3 0 1 0 0 6 3 3 0 0 0 0-6 M3 20c0-4 2-7 5-7s5 3 5 7 M11 20c0-4 2-7 5-7s5 3 5 7",
    "link": "M9 15l6-6 M7 17H5a4 4 0 0 1 0-8h4 M15 7h4a4 4 0 0 1 0 8h-4",
    "move": "M12 2v20 M2 12h20 M12 2l-3 3 M12 2l3 3 M22 12l-3-3 M22 12l-3 3 M12 22l-3-3 M12 22l3-3 M2 12l3-3 M2 12l3 3",
    "delete": "M5 7h14 M9 7V4h6v3 M7 7l1 14h8l1-14 M10 11v6 M14 11v6",
    "fit": "M4 9V4h5 M15 4h5v5 M20 15v5h-5 M9 20H4v-5",
    "zoom_in": "M10 4a6 6 0 1 0 0 12 6 6 0 0 0 0-12 M14 14l6 6 M10 7v6 M7 10h6",
}


def icon(name: str, color: str = "#F8FAFC", size: int = 24) -> QIcon:
    path = PATHS[name]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{path}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)
