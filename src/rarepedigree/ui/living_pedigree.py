"""Editorial, clinically grounded animated pedigree for the Welcome screen."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from PySide6.QtCore import Property, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget


@dataclass(frozen=True)
class WelcomePerson:
    x: float
    y: float
    shape: str
    identifier: str
    detail: str
    affected: bool = False
    proband: bool = False


class LivingPedigree(QWidget):
    """A restrained pedigree that reveals relationships instead of decorative particles."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("living-pedigree")
        self.setMinimumSize(390, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setAccessibleName("Ilustração científica de heredograma")
        self._progress = 1.0
        self._elapsed = 0.0
        self._hover_x = 0.0
        self._hover_y = 0.0
        self._hovered: int | None = None
        self._theme = "midnight"
        self._active = False
        self._reduced_motion = False
        self._last_tick = time.perf_counter()
        self._frame_times: list[float] = []
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._advance)
        self.people = (
            WelcomePerson(0.20, 0.17, "square", "I-1", "Avô materno"),
            WelcomePerson(0.36, 0.17, "circle", "I-2", "Avó materna"),
            WelcomePerson(0.67, 0.15, "square", "I-3", "Avô paterno"),
            WelcomePerson(0.83, 0.15, "circle", "I-4", "Avó paterna"),
            WelcomePerson(0.29, 0.47, "circle", "II-1", "Mãe"),
            WelcomePerson(0.59, 0.47, "square", "II-2", "Pai"),
            WelcomePerson(0.75, 0.47, "circle", "II-3", "Tia paterna"),
            WelcomePerson(
                0.45, 0.78, "square", "III-1", "Probando · avaliação clínica", True, True
            ),
            WelcomePerson(0.61, 0.78, "diamond", "III-2", "Irmão · sexo não especificado"),
        )

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, value))
        self.update()

    progress = Property(float, get_progress, set_progress)
    introProgress = Property(float, get_progress, set_progress)

    def get_bob_offset(self) -> float:
        return 0.0

    def set_bob_offset(self, _value: float) -> None:
        pass

    bobOffset = Property(float, get_bob_offset, set_bob_offset)

    def get_hover_x(self) -> float:
        return self._hover_x

    def get_hover_y(self) -> float:
        return self._hover_y

    hoverX = Property(float, get_hover_x)
    hoverY = Property(float, get_hover_y)

    @property
    def timer_active(self) -> bool:
        return self._timer.isActive()

    @property
    def average_fps(self) -> float:
        if not self._frame_times:
            return 0.0
        mean = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / mean if mean else 0.0

    def set_intro_progress(self, value: float) -> None:
        self.set_progress(value)

    def set_theme(self, theme: str) -> None:
        self._theme = "light" if theme == "light" else "midnight"
        self.update()

    def start(self, reduced_motion: bool = False) -> None:
        self._reduced_motion = reduced_motion
        self._active = not reduced_motion
        self._last_tick = time.perf_counter()
        if self._active and self.isVisible():
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def stop(self) -> None:
        self._active = False
        self._timer.stop()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._active and not self._reduced_motion:
            self._last_tick = time.perf_counter()
            self._timer.start()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def _advance(self) -> None:
        now = time.perf_counter()
        delta = min(0.08, now - self._last_tick)
        self._last_tick = now
        self._frame_times = [*self._frame_times[-89:], delta]
        self._elapsed += delta
        self.update()

    def _area(self) -> QRectF:
        return QRectF(34, 18, max(1, self.width() - 68), max(1, self.height() - 46))

    def _point(self, person: WelcomePerson) -> QPointF:
        area = self._area()
        return QPointF(area.left() + person.x * area.width(), area.top() + person.y * area.height())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._reduced_motion:
            return super().mouseMoveEvent(event)
        normalized_x = event.position().x() / max(1, self.width()) - 0.5
        normalized_y = event.position().y() / max(1, self.height()) - 0.5
        self._hover_x = max(-6.0, min(6.0, normalized_x * 12))
        self._hover_y = max(-5.0, min(5.0, normalized_y * 10))
        nearest = min(
            range(len(self.people)),
            key=lambda index: (
                self._point(self.people[index]) - event.position()
            ).manhattanLength(),
        )
        nearest_distance = (
            self._point(self.people[nearest]) - event.position()
        ).manhattanLength()
        self._hovered = nearest if nearest_distance < 58 else None
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover_x = 0.0
        self._hover_y = 0.0
        self._hovered = None
        self.update()
        super().leaveEvent(event)

    def _draw_segment(self, painter: QPainter, start: QPointF, end: QPointF, amount: float) -> None:
        if amount <= 0:
            return
        painter.drawLine(start, start + (end - start) * min(1.0, amount))

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ink = QColor("#B6C2CF" if self._theme == "midnight" else "#405261")
        muted = QColor("#728399" if self._theme == "midnight" else "#71808B")
        accent = QColor("#6FB5C8" if self._theme == "midnight" else "#167E96")
        paper = QColor("#0C1427" if self._theme == "midnight" else "#EAF3F8")
        affected = QColor("#C8765F" if self._theme == "midnight" else "#B6533C")
        painter.setPen(QPen(ink, 1.6))
        points = [self._point(person) for person in self.people]
        # Union lines and descent buses are deliberately orthogonal and asymmetric.
        maternal_mid_x = (points[0].x() + points[1].x()) / 2
        paternal_mid_x = (points[2].x() + points[3].x()) / 2
        parents_mid_x = (points[4].x() + points[5].x()) / 2
        segments = (
            (points[0], points[1]),
            (
                QPointF(maternal_mid_x, points[0].y()),
                QPointF(maternal_mid_x, points[4].y() - 42),
            ),
            (
                QPointF(maternal_mid_x, points[4].y() - 42),
                QPointF(points[4].x(), points[4].y() - 42),
            ),
            (QPointF(points[4].x(), points[4].y() - 42), points[4]),
            (points[2], points[3]),
            (
                QPointF(paternal_mid_x, points[2].y()),
                QPointF(paternal_mid_x, points[5].y() - 42),
            ),
            (
                QPointF(points[5].x(), points[5].y() - 42),
                QPointF(points[6].x(), points[6].y() - 42),
            ),
            (QPointF(points[5].x(), points[5].y() - 42), points[5]),
            (QPointF(points[6].x(), points[6].y() - 42), points[6]),
            (points[4], points[5]),
            (
                QPointF(parents_mid_x, points[4].y()),
                QPointF(parents_mid_x, points[7].y() - 40),
            ),
            (
                QPointF(points[7].x(), points[7].y() - 40),
                QPointF(points[8].x(), points[8].y() - 40),
            ),
            (QPointF(points[7].x(), points[7].y() - 40), points[7]),
            (QPointF(points[8].x(), points[8].y() - 40), points[8]),
        )
        reveal = self._progress * (len(segments) + 3)
        for index, (start, end) in enumerate(segments):
            self._draw_segment(painter, start, end, reveal - index)
        node_start = max(0.0, self._progress * 1.7 - 0.55)
        for index, (person, center) in enumerate(zip(self.people, points, strict=True)):
            opacity = max(0.0, min(1.0, node_start * 2.0 - index * 0.055))
            if not opacity:
                continue
            radius = 18.0
            if index == self._hovered:
                radius += 2.5 + math.sin(self._elapsed * 3.0) * 1.0
            rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
            painter.setOpacity(opacity)
            node_pen = accent if index == self._hovered else ink
            painter.setPen(QPen(node_pen, 2.2 if person.proband else 1.5))
            painter.setBrush(affected if person.affected else paper)
            if person.shape == "circle":
                painter.drawEllipse(rect)
            elif person.shape == "diamond":
                path = QPainterPath(center + QPointF(0, -radius))
                path.lineTo(center + QPointF(radius, 0))
                path.lineTo(center + QPointF(0, radius))
                path.lineTo(center + QPointF(-radius, 0))
                path.closeSubpath()
                painter.drawPath(path)
            else:
                painter.drawRect(rect)
            if person.proband:
                painter.setPen(QPen(accent, 1.7))
                painter.drawLine(center + QPointF(-34, 31), center + QPointF(-20, 17))
                painter.drawLine(center + QPointF(-20, 17), center + QPointF(-25, 18))
                painter.drawLine(center + QPointF(-20, 17), center + QPointF(-21, 22))
            painter.setPen(muted)
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            label_rect = QRectF(center.x() - 42, center.y() + 23, 84, 18)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, person.identifier)
        painter.setOpacity(1.0)
        generations = (("I", points[0].y()), ("II", points[4].y()), ("III", points[7].y()))
        painter.setPen(muted)
        font = QFont(painter.font())
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        for label, y in generations:
            painter.drawText(QPointF(self._area().left(), y + 5), label)
        if self._hovered is not None:
            person = self.people[self._hovered]
            anchor = points[self._hovered]
            width = 188.0
            left = min(self.width() - width - 12, anchor.x() + 28)
            top = max(12.0, anchor.y() - 42)
            card = QRectF(left, top, width, 50)
            painter.setPen(QPen(QColor("#506277"), 1.0))
            painter.setBrush(QColor("#162238" if self._theme == "midnight" else "#FFFFFF"))
            painter.drawRoundedRect(card, 4, 4)
            painter.setPen(ink)
            painter.drawText(card.adjusted(10, 6, -8, -25), person.identifier)
            painter.setPen(muted)
            painter.drawText(card.adjusted(10, 24, -8, -5), person.detail)
