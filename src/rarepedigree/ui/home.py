"""Integrated premium home screen and privacy-safe recent-project metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import (
    Property,
    QAbstractAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSettings,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.ui.i18n import language_manager, tr
from rarepedigree.ui.icons import icon


@dataclass(frozen=True)
class RecentProject:
    title: str
    path: Path
    last_opened: str

    @property
    def available(self) -> bool:
        return self.path.is_file()


class RecentProjectsStore:
    """Store paths and display metadata only; never project clinical data."""

    KEY = "recent_projects/v1"
    MAX_ITEMS = 8

    def __init__(self, settings: QSettings | None = None) -> None:
        self.settings = settings or QSettings()

    def projects(self) -> list[RecentProject]:
        try:
            values = json.loads(self.settings.value(self.KEY, "[]", str))
        except (TypeError, json.JSONDecodeError):
            values = []
        result = []
        for value in values if isinstance(values, list) else []:
            if not isinstance(value, dict) or not value.get("path"):
                continue
            path = Path(value["path"])
            result.append(
                RecentProject(
                    str(value.get("title") or path.stem),
                    path,
                    str(value.get("last_opened") or ""),
                )
            )
        return result[: self.MAX_ITEMS]

    def add(self, path: Path, title: str = "") -> None:
        resolved = path.expanduser().resolve()
        recent = RecentProject(
            title.strip() or resolved.name.removesuffix(".rps.json"),
            resolved,
            datetime.now(UTC).isoformat(timespec="seconds"),
        )
        old = [item for item in self.projects() if item.path != resolved]
        self._write([recent, *old][: self.MAX_ITEMS])

    def remove(self, path: Path) -> None:
        resolved = path.expanduser().resolve()
        self._write([item for item in self.projects() if item.path != resolved])

    def clear(self) -> None:
        self.settings.remove(self.KEY)

    def _write(self, projects: list[RecentProject]) -> None:
        data = [
            {"title": item.title, "path": str(item.path), "last_opened": item.last_opened}
            for item in projects
        ]
        self.settings.setValue(self.KEY, json.dumps(data, ensure_ascii=False))


class PedigreeIllustration(QWidget):
    """Vector pedigree whose progressive reveal does not block interaction."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._progress = 1.0
        self._bob_offset = 0.0
        self._hover_x = 0.0
        self._hover_y = 0.0
        self._motion_enabled = True
        self._pointer_position: QPointF | None = None
        self.setMouseTracking(True)
        self.setMinimumSize(390, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._hover_x_animation = QPropertyAnimation(self, b"hoverX", self)
        self._hover_y_animation = QPropertyAnimation(self, b"hoverY", self)
        for animation in (self._hover_x_animation, self._hover_y_animation):
            animation.setDuration(220)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, value))
        self.update()

    progress = Property(float, get_progress, set_progress)

    def get_bob_offset(self) -> float:
        return self._bob_offset

    def set_bob_offset(self, value: float) -> None:
        self._bob_offset = value
        self.update()

    bobOffset = Property(float, get_bob_offset, set_bob_offset)

    def get_hover_x(self) -> float:
        return self._hover_x

    def set_hover_x(self, value: float) -> None:
        self._hover_x = value
        self.update()

    hoverX = Property(float, get_hover_x, set_hover_x)

    def get_hover_y(self) -> float:
        return self._hover_y

    def set_hover_y(self, value: float) -> None:
        self._hover_y = value
        self.update()

    hoverY = Property(float, get_hover_y, set_hover_y)

    def set_motion_enabled(self, enabled: bool) -> None:
        self._motion_enabled = enabled
        if not enabled:
            self._pointer_position = None
            self._animate_hover_to(0.0, 0.0)

    def _animate_hover_to(self, x: float, y: float) -> None:
        for animation, start, end in (
            (self._hover_x_animation, self._hover_x, x),
            (self._hover_y_animation, self._hover_y, y),
        ):
            animation.stop()
            animation.setStartValue(start)
            animation.setEndValue(end)
            animation.start()

    def mouseMoveEvent(self, event) -> None:
        self._pointer_position = event.position()
        if self._motion_enabled and self.width() and self.height():
            normalized_x = (event.position().x() / self.width() - 0.5) * 2.0
            normalized_y = (event.position().y() / self.height() - 0.5) * 2.0
            self._animate_hover_to(normalized_x * 6.0, normalized_y * 5.0)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self._pointer_position = None
        self._animate_hover_to(0.0, 0.0)
        super().leaveEvent(event)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = self.rect().adjusted(25, 20, -25, -20)
        scale = min(area.width() / 520.0, area.height() / 310.0)
        origin = QPointF(
            area.center().x() - 260 * scale,
            area.center().y() - 155 * scale + self._bob_offset + self._hover_y,
        )
        origin.setX(origin.x() + self._hover_x)

        def point(x: float, y: float) -> QPointF:
            return origin + QPointF(x * scale, y * scale)

        painter.setPen(QPen(QColor("#6EC6E8"), max(2.0, 2.4 * scale)))
        segments = [
            (point(165, 72), point(355, 72)),
            (point(260, 72), point(260, 142)),
            (point(135, 142), point(385, 142)),
            (point(135, 142), point(135, 200)),
            (point(260, 142), point(260, 200)),
            (point(385, 142), point(385, 200)),
            (point(260, 240), point(260, 282)),
        ]
        reveal = self._progress * len(segments)
        for index, (start, end) in enumerate(segments):
            fraction = max(0.0, min(1.0, reveal - index))
            if fraction:
                painter.drawLine(start, start + (end - start) * fraction)
        nodes = [
            (165, 72, "square", 0.06),
            (355, 72, "circle", 0.15),
            (135, 220, "circle", 0.46),
            (260, 220, "square", 0.56),
            (385, 220, "diamond", 0.66),
            (260, 290, "circle", 0.80),
        ]
        for x, y, shape, threshold in nodes:
            opacity = max(0.0, min(1.0, (self._progress - threshold) / 0.16))
            if not opacity:
                continue
            size = 42 * scale * (0.75 + opacity * 0.25)
            center = point(x, y)
            rect = QRectF(center.x() - size / 2, center.y() - size / 2, size, size)
            painter.setOpacity(opacity)
            node_center = point(x, y)
            hovered = (
                self._pointer_position is not None
                and (node_center - self._pointer_position).manhattanLength() < 58
            )
            if hovered and self._motion_enabled:
                painter.setPen(QPen(QColor("#B6F0FF"), 5.0))
                painter.setBrush(QColor("#203C68"))
            else:
                painter.setPen(QPen(QColor("#7C8CFF" if x == 260 else "#6EC6E8"), 2.5))
                painter.setBrush(QColor("#111D39" if x == 260 else "#17294B"))
            if shape == "circle":
                painter.drawEllipse(rect)
            elif shape == "diamond":
                path = QPainterPath()
                path.moveTo(center.x(), rect.top())
                path.lineTo(rect.right(), center.y())
                path.lineTo(center.x(), rect.bottom())
                path.lineTo(rect.left(), center.y())
                path.closeSubpath()
                painter.drawPath(path)
            else:
                painter.drawRoundedRect(rect, 3, 3)
        painter.setOpacity(1.0)


class WelcomeActionCard(QFrame):
    clicked = Signal()

    def __init__(self, icon_name: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("welcome-action-card")
        self.setMinimumHeight(88)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 14, 12)
        layout.setSpacing(13)
        self._icon_name = icon_name
        self._motion_enabled = True
        self.glyph = QLabel()
        self.glyph.setPixmap(icon(icon_name, "#62D4FF", 28).pixmap(28, 28))
        self.glyph.setFixedSize(42, 42)
        self.glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.glyph.setObjectName("welcome-card-icon")
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(180)
        self._hover_animation.setStartValue(28.0)
        self._hover_animation.setEndValue(32.0)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.valueChanged.connect(self._set_icon_size)
        copy = QVBoxLayout()
        copy.setSpacing(2)
        self.title_label = QLabel()
        self.title_label.setObjectName("welcome-card-title")
        self.description_label = QLabel()
        self.description_label.setObjectName("welcome-card-description")
        self.description_label.setWordWrap(True)
        copy.addWidget(self.title_label)
        copy.addWidget(self.description_label)
        layout.addWidget(self.glyph)
        layout.addLayout(copy, 1)
        self.button = QPushButton()
        self.button.setObjectName("welcome-card-hit-target")
        self.button.setIcon(icon("open", "#B6C6DD", 18))
        self.button.clicked.connect(self.clicked)
        layout.addWidget(self.button)

    def set_text(self, title: str, description: str) -> None:
        self.title_label.setText(title)
        self.description_label.setText(description)
        self.button.setAccessibleName(title)
        self.button.setToolTip(title)
        self.setAccessibleName(title)
        self.setAccessibleDescription(description)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(
            event.position().toPoint()
        ):
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def enterEvent(self, event) -> None:
        if self._motion_enabled:
            self._hover_animation.setDirection(QAbstractAnimation.Direction.Forward)
            self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover_animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._hover_animation.start()
        super().leaveEvent(event)

    def _set_icon_size(self, value: float) -> None:
        size = round(value)
        self.glyph.setPixmap(icon(self._icon_name, "#62D4FF", size).pixmap(size, size))

    def set_motion_enabled(self, enabled: bool) -> None:
        self._motion_enabled = enabled
        if not enabled:
            self._hover_animation.stop()
            self._set_icon_size(28.0)


class WelcomeScreen(QWidget):
    """Persistent Home page embedded in the existing main window."""

    newRequested = Signal()
    openRequested = Signal()
    recentRequested = Signal(Path)

    def __init__(self, store: RecentProjectsStore | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("welcome-screen")
        self.store = store or RecentProjectsStore()
        self._animations = QParallelAnimationGroup(self)
        shell = QHBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        self.hero = QFrame()
        self.hero.setObjectName("welcome-hero")
        hero = QVBoxLayout(self.hero)
        hero.setContentsMargins(54, 42, 42, 38)
        brand_row = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(icon("logo", "#56D6FF", 42).pixmap(42, 42))
        brand = QLabel("RarePedigree Studio")
        brand.setObjectName("welcome-brand")
        brand_row.addWidget(logo)
        brand_row.addSpacing(9)
        brand_row.addWidget(brand)
        brand_row.addStretch()
        hero.addLayout(brand_row)
        self.tagline = QLabel()
        self.tagline.setObjectName("welcome-tagline")
        hero.addWidget(self.tagline)
        self.illustration = PedigreeIllustration()
        self._idle_animation = QPropertyAnimation(self.illustration, b"bobOffset", self)
        self._idle_animation.setDuration(4200)
        self._idle_animation.setLoopCount(-1)
        self._idle_animation.setKeyValueAt(0.0, 0.0)
        self._idle_animation.setKeyValueAt(0.25, -5.0)
        self._idle_animation.setKeyValueAt(0.5, 0.0)
        self._idle_animation.setKeyValueAt(0.75, 5.0)
        self._idle_animation.setKeyValueAt(1.0, 0.0)
        self._idle_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        hero.addWidget(self.illustration, 1)
        self.privacy = QLabel()
        self.privacy.setWordWrap(True)
        self.privacy.setObjectName("welcome-privacy")
        hero.addWidget(self.privacy)
        self.actions = QFrame()
        self.actions.setObjectName("welcome-actions")
        action_layout = QVBoxLayout(self.actions)
        action_layout.setContentsMargins(52, 42, 52, 36)
        action_layout.setSpacing(12)
        action_layout.addStretch()
        self.heading = QLabel()
        self.heading.setObjectName("welcome-heading")
        self.intro = QLabel()
        self.intro.setObjectName("welcome-intro")
        self.intro.setWordWrap(True)
        action_layout.addWidget(self.heading)
        action_layout.addWidget(self.intro)
        action_layout.addSpacing(10)
        self.new_card = WelcomeActionCard("new")
        self.open_card = WelcomeActionCard("open")
        self.recent_card = WelcomeActionCard("save")
        self.new_card.clicked.connect(self.newRequested)
        self.open_card.clicked.connect(self.openRequested)
        self.recent_card.clicked.connect(self.toggle_recent_projects)
        action_layout.addWidget(self.new_card)
        action_layout.addWidget(self.open_card)
        action_layout.addWidget(self.recent_card)
        self.recent_panel = QFrame()
        self.recent_panel.setObjectName("recent-projects-panel")
        recent_layout = QVBoxLayout(self.recent_panel)
        recent_layout.setContentsMargins(10, 8, 10, 8)
        self.recent_list = QVBoxLayout()
        recent_layout.addLayout(self.recent_list)
        self.clear_recent_button = QPushButton()
        self.clear_recent_button.clicked.connect(self.clear_recent_projects)
        recent_layout.addWidget(self.clear_recent_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.recent_panel.hide()
        action_layout.addWidget(self.recent_panel)
        action_layout.addStretch()
        shell.addWidget(self.hero, 11)
        shell.addWidget(self.actions, 9)
        language_manager.languageChanged.connect(self.retranslate_ui)
        self.retranslate_ui()

    def start_animation(self, reduced_motion: bool = False) -> None:
        self._animations.stop()
        self._idle_animation.stop()
        self.illustration.set_bob_offset(0.0)
        for card in (self.new_card, self.open_card, self.recent_card):
            card.set_motion_enabled(not reduced_motion)
        self._animations.deleteLater()
        self._animations = QParallelAnimationGroup(self)
        if reduced_motion:
            self.illustration.set_motion_enabled(False)
            self.illustration.set_progress(1.0)
            for widget in (
                self.heading,
                self.intro,
                self.new_card,
                self.open_card,
                self.recent_card,
            ):
                effect = widget.graphicsEffect()
                if isinstance(effect, QGraphicsOpacityEffect):
                    effect.setOpacity(1.0)
            return
        self.illustration.set_motion_enabled(True)
        self.illustration.set_progress(0.0)
        drawing = QPropertyAnimation(self.illustration, b"progress", self)
        drawing.setDuration(2800)
        drawing.setStartValue(0.0)
        drawing.setEndValue(1.0)
        drawing.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animations.addAnimation(drawing)
        for index, widget in enumerate(
            (self.heading, self.intro, self.new_card, self.open_card, self.recent_card)
        ):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(1050 + index * 170)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._animations.addAnimation(animation)
        self._animations.finished.connect(self._start_idle_animation)
        self._animations.start()

    def _start_idle_animation(self) -> None:
        if self.isVisible():
            self._idle_animation.start()

    def stop_animation(self) -> None:
        self._animations.stop()
        self._idle_animation.stop()
        self.illustration.set_progress(1.0)
        self.illustration.set_bob_offset(0.0)
        for widget in (self.heading, self.intro, self.new_card, self.open_card, self.recent_card):
            effect = widget.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                effect.setOpacity(1.0)

    def set_theme(self, theme: str) -> None:
        self.setProperty("welcomeTheme", "light" if theme == "light" else "midnight")
        self.style().unpolish(self)
        self.style().polish(self)
        for child in self.findChildren(QWidget):
            child.style().unpolish(child)
            child.style().polish(child)

    def toggle_recent_projects(self) -> None:
        self.refresh_recent_projects()
        self.recent_panel.setVisible(not self.recent_panel.isVisible())

    def refresh_recent_projects(self) -> None:
        while self.recent_list.count():
            item = self.recent_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        projects = self.store.projects()
        if not projects:
            empty = QLabel(tr("Nenhum projeto recente"))
            empty.setObjectName("recent-empty")
            self.recent_list.addWidget(empty)
        for project in projects:
            row = QFrame()
            row.setObjectName("recent-project-row")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(7, 5, 5, 5)
            copy = QVBoxLayout()
            title = QLabel(project.title)
            title.setObjectName("recent-project-title")
            path = QLabel(str(project.path))
            path.setObjectName("recent-project-path")
            path.setToolTip(str(project.path))
            copy.addWidget(title)
            copy.addWidget(path)
            layout.addLayout(copy, 1)
            open_button = QPushButton(tr("Abrir"))
            open_button.setEnabled(project.available)
            open_button.clicked.connect(
                lambda _checked=False, value=project.path: self.recentRequested.emit(value)
            )
            remove = QToolButton()
            remove.setText("\u2715")
            remove.setToolTip(tr("Remover da lista"))
            remove.clicked.connect(
                lambda _checked=False, value=project.path: self.remove_recent_project(value)
            )
            layout.addWidget(open_button)
            layout.addWidget(remove)
            if not project.available:
                row.setProperty("unavailable", True)
                title.setText(f"{project.title} — {tr('indisponível')}")
            self.recent_list.addWidget(row)
        self.clear_recent_button.setVisible(bool(projects))

    def remove_recent_project(self, path: Path) -> None:
        self.store.remove(path)
        self.refresh_recent_projects()

    def clear_recent_projects(self) -> None:
        self.store.clear()
        self.refresh_recent_projects()

    def retranslate_ui(self, _language: str | None = None) -> None:
        self.tagline.setText(tr("Genética • Família • Descoberta"))
        self.privacy.setText(
            tr("Privacidade por padrão: seus projetos permanecem neste computador.")
        )
        self.heading.setText(tr("Bem-vindo ao seu espaço científico"))
        self.intro.setText(tr("Crie, documente e explore heredogramas clínicos com clareza."))
        self.new_card.set_text(
            tr("Nova família"), tr("Inicie um heredograma com o assistente de projeto.")
        )
        self.open_card.set_text(
            tr("Abrir projeto"), tr("Carregue um arquivo RarePedigree existente.")
        )
        self.recent_card.set_text(
            tr("Projetos recentes"), tr("Retome rapidamente um trabalho local.")
        )
        self.clear_recent_button.setText(tr("Limpar lista"))
        if self.recent_panel.isVisible():
            self.refresh_recent_projects()
