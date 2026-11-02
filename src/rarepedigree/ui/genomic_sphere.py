"""Efficient QPainter pseudo-3D genomic network for the native Welcome screen."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from PySide6.QtCore import Property, QPointF, QRectF, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QSizePolicy, QWidget


@dataclass(frozen=True)
class SphereParameters:
    fps_limit: int = 60
    animation_speed: float = 0.55
    deformation: float = 0.075
    spatial_frequency: float = 2.2
    rotation_speed: float = 0.16
    cursor_amplitude: float = 0.20
    depth: float = 3.4

    @classmethod
    def from_settings(cls, settings: QSettings) -> SphereParameters:
        fps = max(15, min(60, settings.value("welcome/sphere_fps", 60, int)))
        return cls(
            fps_limit=fps,
            animation_speed=settings.value("welcome/sphere_animation_speed", 0.55, float),
            deformation=settings.value("welcome/sphere_deformation", 0.075, float),
            spatial_frequency=settings.value("welcome/sphere_frequency", 2.2, float),
            rotation_speed=settings.value("welcome/sphere_rotation_speed", 0.16, float),
            cursor_amplitude=settings.value("welcome/sphere_cursor_amplitude", 0.20, float),
            depth=settings.value("welcome/sphere_depth", 3.4, float),
        )


class GenomicSphere(QWidget):
    """Interactive organic network projected from stable three-dimensional geometry."""

    frameRendered = Signal(float)
    interactionChanged = Signal(str)

    def __init__(self, settings: QSettings | None = None, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings or QSettings()
        self.parameters = SphereParameters.from_settings(self.settings)
        self.setObjectName("genomic-sphere")
        self.setMinimumSize(360, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAccessibleName("Genomic Sphere — decorative genetic relationship network")
        self._vertices = self._fibonacci_vertices(74)
        self._edges = self._nearest_edges(self._vertices, 3)
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.setInterval(round(1000 / self.parameters.fps_limit))
        self._timer.timeout.connect(self._advance_frame)
        self._last_tick = time.perf_counter()
        self._frame_times: list[float] = []
        self._elapsed = 0.0
        self._rotation_x = -0.16
        self._rotation_y = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._cursor_y = 0.0
        self._inertia_x = 0.0
        self._inertia_y = 0.0
        self._drag_origin: QPointF | None = None
        self._drag_rotation = (0.0, 0.0)
        self._last_drag_delta = QPointF()
        self._pulse = 0.0
        self._intro_progress = 1.0
        self._legacy_bob_offset = 0.0
        self._reduced_motion = False
        self._theme = "midnight"
        self._active = False

    @staticmethod
    def _fibonacci_vertices(count: int) -> tuple[tuple[float, float, float], ...]:
        golden_angle = math.pi * (3.0 - math.sqrt(5.0))
        vertices = []
        for index in range(count):
            y = 1.0 - 2.0 * index / (count - 1)
            radius = math.sqrt(max(0.0, 1.0 - y * y))
            angle = golden_angle * index
            vertices.append((math.cos(angle) * radius, y, math.sin(angle) * radius))
        return tuple(vertices)

    @staticmethod
    def _nearest_edges(
        vertices: tuple[tuple[float, float, float], ...], neighbours: int
    ) -> tuple[tuple[int, int], ...]:
        edges: set[tuple[int, int]] = set()
        for index, vertex in enumerate(vertices):
            distances = sorted(
                (
                    sum((vertex[axis] - other[axis]) ** 2 for axis in range(3)),
                    other_index,
                )
                for other_index, other in enumerate(vertices)
                if other_index != index
            )
            for _distance, other_index in distances[:neighbours]:
                edges.add(tuple(sorted((index, other_index))))
        return tuple(sorted(edges))

    def get_intro_progress(self) -> float:
        return self._intro_progress

    def set_intro_progress(self, value: float) -> None:
        self._intro_progress = max(0.0, min(1.0, value))
        self.update()

    introProgress = Property(float, get_intro_progress, set_intro_progress)
    progress = Property(float, get_intro_progress, set_intro_progress)

    def get_bob_offset(self) -> float:
        return self._legacy_bob_offset

    def set_bob_offset(self, value: float) -> None:
        self._legacy_bob_offset = value

    bobOffset = Property(float, get_bob_offset, set_bob_offset)

    def get_hover_x(self) -> float:
        amplitude = self.parameters.cursor_amplitude or 1.0
        return self._target_y / amplitude * 6.0

    def get_hover_y(self) -> float:
        amplitude = self.parameters.cursor_amplitude * 0.65 or 1.0
        return (self._target_x + 0.16) / amplitude * 5.0

    hoverX = Property(float, get_hover_x)
    hoverY = Property(float, get_hover_y)

    @property
    def fallback_mode(self) -> bool:
        return True

    @property
    def timer_active(self) -> bool:
        return self._timer.isActive()

    @property
    def average_fps(self) -> float:
        if not self._frame_times:
            return 0.0
        average = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / average if average else 0.0

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
        self._drag_origin = None

    def set_economy_mode(self, enabled: bool) -> None:
        fps = 30 if enabled else self.parameters.fps_limit
        self._timer.setInterval(round(1000 / fps))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._active and not self._reduced_motion:
            self._last_tick = time.perf_counter()
            self._timer.start()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def _advance_frame(self) -> None:
        now = time.perf_counter()
        delta = min(0.05, max(0.0, now - self._last_tick))
        self._last_tick = now
        self._frame_times.append(delta)
        self._frame_times = self._frame_times[-120:]
        self._elapsed += delta * self.parameters.animation_speed
        smoothing = min(1.0, delta * 4.0)
        self._rotation_x += (self._target_x - self._rotation_x) * smoothing
        self._rotation_y += self.parameters.rotation_speed * delta
        self._cursor_y += (self._target_y - self._cursor_y) * smoothing
        if self._drag_origin is None:
            self._rotation_x += self._inertia_x * delta
            self._rotation_y += self._inertia_y * delta
            self._inertia_x *= 0.94
            self._inertia_y *= 0.94
        self._pulse = max(0.0, self._pulse - delta * 0.8)
        self.update()
        self.frameRendered.emit(delta)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._reduced_motion:
            return super().mouseMoveEvent(event)
        if self._drag_origin is not None:
            delta = event.position() - self._drag_origin
            self._rotation_y = self._drag_rotation[1] + delta.x() * 0.008
            self._rotation_x = self._drag_rotation[0] + delta.y() * 0.008
            self._last_drag_delta = delta
            self.interactionChanged.emit("drag")
        elif self.width() and self.height():
            x = (event.position().x() / self.width() - 0.5) * 2.0
            y = (event.position().y() / self.height() - 0.5) * 2.0
            self._target_y = x * self.parameters.cursor_amplitude
            self._target_x = -0.16 + y * self.parameters.cursor_amplitude * 0.65
            self.interactionChanged.emit("hover")
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._reduced_motion:
            self._drag_origin = event.position()
            self._drag_rotation = (self._rotation_x, self._rotation_y)
            self._last_drag_delta = QPointF()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._drag_origin is not None:
            distance = self._last_drag_delta.manhattanLength()
            if distance < 5:
                self._pulse = 1.0
                self.interactionChanged.emit("pulse")
            else:
                self._inertia_y = max(-1.2, min(1.2, self._last_drag_delta.x() * 0.015))
                self._inertia_x = max(-1.2, min(1.2, self._last_drag_delta.y() * 0.015))
            self._drag_origin = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:
        if self._drag_origin is None:
            self._target_x = -0.16
            self._target_y = 0.0
        super().leaveEvent(event)

    @staticmethod
    def _rotate(
        vertex: tuple[float, float, float], rotation_x: float, rotation_y: float
    ) -> tuple[float, float, float]:
        x, y, z = vertex
        cy, sy = math.cos(rotation_y), math.sin(rotation_y)
        x, z = x * cy + z * sy, -x * sy + z * cy
        cx, sx = math.cos(rotation_x), math.sin(rotation_x)
        y, z = y * cx - z * sx, y * sx + z * cx
        return x, y, z

    def _projected(self) -> list[tuple[QPointF, float, float]]:
        projected = []
        radius = min(self.width(), self.height()) * 0.335 * (0.88 + self._intro_progress * 0.12)
        center = QPointF(self.width() * 0.5, self.height() * 0.51)
        for index, base in enumerate(self._vertices):
            if self._reduced_motion:
                deformation = 1.0
            else:
                phase = self._elapsed * 1.7 + index * 0.17
                organic = (
                    math.sin(base[0] * self.parameters.spatial_frequency + phase)
                    + math.sin(base[1] * (self.parameters.spatial_frequency + 0.7) - phase * 0.7)
                    + math.cos(base[2] * (self.parameters.spatial_frequency - 0.4) + phase * 0.45)
                ) / 3.0
                deformation = 1.0 + organic * self.parameters.deformation
            vertex = tuple(component * deformation for component in base)
            x, y, z = self._rotate(vertex, self._rotation_x, self._rotation_y + self._cursor_y)
            perspective = self.parameters.depth / (self.parameters.depth - z)
            projected.append(
                (
                    QPointF(
                        center.x() + x * radius * perspective,
                        center.y() + y * radius * perspective,
                    ),
                    z,
                    perspective,
                )
            )
        return projected

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        projected = self._projected()
        opacity = self._intro_progress
        if self._theme == "light":
            line = QColor("#15779A")
            node = QColor("#086B8E")
            glow = QColor("#6B5CD6")
        else:
            line = QColor("#55C7E8")
            node = QColor("#8AE6FA")
            glow = QColor("#8374FF")
        background = QRadialGradient(self.rect().center(), min(self.width(), self.height()) * 0.46)
        halo = QColor(glow)
        halo.setAlpha(round(22 * opacity))
        background.setColorAt(0.0, halo)
        halo.setAlpha(0)
        background.setColorAt(1.0, halo)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawEllipse(QRectF(self.rect()))
        for first, second in sorted(
            self._edges, key=lambda edge: projected[edge[0]][1] + projected[edge[1]][1]
        ):
            start, start_z, _ = projected[first]
            end, end_z, _ = projected[second]
            depth = max(0.0, min(1.0, ((start_z + end_z) / 2.0 + 1.0) / 2.0))
            color = QColor(line)
            color.setAlpha(round((28 + depth * 112) * opacity))
            painter.setPen(QPen(color, 0.65 + depth * 0.75))
            painter.drawLine(start, end)
        for index in sorted(range(len(projected)), key=lambda item: projected[item][1]):
            point, z, perspective = projected[index]
            depth = max(0.0, min(1.0, (z + 1.0) / 2.0))
            radius = (1.4 + depth * 2.7) * perspective
            if self._pulse and index % 7 == 0:
                pulse_color = QColor(glow)
                pulse_color.setAlpha(round(90 * self._pulse * opacity))
                painter.setBrush(pulse_color)
                painter.setPen(Qt.PenStyle.NoPen)
                pulse_radius = radius + 7.0 * self._pulse
                painter.drawEllipse(point, pulse_radius, pulse_radius)
            color = QColor(node)
            color.setAlpha(round((75 + depth * 180) * opacity))
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(point, radius, radius)
