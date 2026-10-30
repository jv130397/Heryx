"""Reusable presentation components for the Scientific Workspace."""

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from rarepedigree.ui.i18n import tr
from rarepedigree.ui.icons import icon


class ToolRailButton(QToolButton):
    def __init__(
        self, action: QAction, icon_name: str, parent=None, expanded: bool = False
    ) -> None:
        super().__init__(parent)
        self.setDefaultAction(action)
        self.setIcon(icon(icon_name))
        self.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            if expanded
            else Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.setFixedHeight(46)
        if not expanded:
            self.setFixedWidth(44)
        self.setAccessibleName(action.text().replace("…", ""))
        self.setToolTip(f"{action.text()} ({action.shortcut().toString()})".rstrip(" ()"))
        self.setProperty("railButton", True)


class SectionHeader(QLabel):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text.upper(), parent)
        self.setProperty("sectionHeader", True)


class EmptyState(QFrame):
    addRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("empty-state")
        self.setMaximumWidth(420)
        self.setMaximumHeight(300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        mark = QLabel("◇")
        mark.setObjectName("empty-mark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel()
        self.title.setObjectName("empty-title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message = QLabel()
        self.message.setWordWrap(True)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button = QPushButton()
        self.button.setObjectName("primary-button")
        self.button.clicked.connect(self.addRequested)
        layout.addWidget(mark)
        layout.addWidget(self.title)
        layout.addWidget(self.message)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.title.setText(tr("Comece um novo heredograma"))
        self.message.setText(
            tr("Adicione o primeiro indivíduo para iniciar a construção familiar.")
        )
        self.button.setText(tr("Adicionar primeiro indivíduo"))


class ZoomControl(QWidget):
    zoomIn = Signal()
    zoomOut = Signal()
    fitRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("zoom-control")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(2)
        minus = QToolButton(text="-")
        plus = QToolButton(text="+")
        fit = QToolButton()
        fit.setIcon(icon("fit", "#334155", 18))
        fit.setToolTip("Ajustar à tela (Ctrl+0)")
        self.label = QLabel("100%")
        self.label.setMinimumWidth(44)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        minus.clicked.connect(self.zoomOut)
        plus.clicked.connect(self.zoomIn)
        fit.clicked.connect(self.fitRequested)
        layout.addWidget(minus)
        layout.addWidget(self.label)
        layout.addWidget(plus)
        layout.addWidget(fit)

    def set_zoom(self, percent: int) -> None:
        self.label.setText(f"{percent}%")


class FamilyMenu(QMenu):
    """Consistent popup for family construction commands."""

    def __init__(self, actions: list[QAction], parent=None) -> None:
        super().__init__(parent)
        self.setAccessibleName("Adicionar familiar")
        self.addActions(actions)


class Toast(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("toast")
        layout = QHBoxLayout(self)
        self.icon = QLabel("✓")
        self.message = QLabel()
        layout.addWidget(self.icon)
        layout.addWidget(self.message)
        self.hide()

    def show_message(self, message: str, level: str = "success") -> None:
        self.icon.setText({"success": "✓", "warning": "!", "error": "x"}[level])
        self.setProperty("level", level)
        self.style().unpolish(self)
        self.style().polish(self)
        self.message.setText(message)
        self.adjustSize()
        if self.parentWidget() is not None:
            self.move(18, self.parentWidget().height() - self.height() - 18)
        self.show()
        self.raise_()
        QTimer.singleShot(3200, self.hide)


class SlidingPanel(QFrame):
    """Overlay drawer that does not permanently consume canvas width."""

    closeRequested = Signal()
    MARGIN = 18

    def __init__(self, content: QWidget, parent=None) -> None:
        super().__init__(parent)
        if parent is not None:
            parent.installEventFilter(self)
        self.setObjectName("properties-drawer")
        self.setMinimumWidth(330)
        self.setFixedWidth(390)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(-5, 6)
        shadow.setColor(QColor(3, 8, 20, 145))
        self.setGraphicsEffect(shadow)
        self._open = False
        self.animation = QPropertyAnimation(self, b"geometry", self)
        self.animation.setDuration(180)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self._hide_if_closed)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 8, 8)
        self.title = QLabel(tr("Propriedades do indivíduo"))
        self.title.setStyleSheet("font-weight: 700;")
        close = QToolButton(text="✕")
        close.setAccessibleName(tr("Fechar"))
        close.clicked.connect(self.close_panel)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(close)
        root.addWidget(header)
        root.addWidget(content, 1)
        self.hide()

    def open_panel(self) -> None:
        if self.parentWidget() is None:
            return
        was_visible = self.isVisible()
        self._open = True
        self.show()
        self.raise_()
        parent_rect = self.parentWidget().rect()
        panel_height = max(240, parent_rect.height() - self.MARGIN * 2)
        start = QRect(
            parent_rect.width() + self.MARGIN,
            self.MARGIN,
            self.width(),
            panel_height,
        )
        end = QRect(
            parent_rect.width() - self.width() - self.MARGIN,
            self.MARGIN,
            self.width(),
            panel_height,
        )
        self.animation.stop()
        self.animation.setStartValue(self.geometry() if was_visible else start)
        self.animation.setEndValue(end)
        self.animation.start()

    def close_panel(self) -> None:
        if self.parentWidget() is None or self.isHidden():
            return
        self._open = False
        parent_rect = self.parentWidget().rect()
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(
            QRect(
                parent_rect.width() + self.MARGIN,
                self.MARGIN,
                self.width(),
                max(240, parent_rect.height() - self.MARGIN * 2),
            )
        )
        self.animation.start()
        self.closeRequested.emit()

    def _hide_if_closed(self) -> None:
        if not self._open:
            self.hide()

    def sync_geometry(self) -> None:
        if self.parentWidget() is None:
            return
        parent_rect = self.parentWidget().rect()
        x = (
            parent_rect.width() - self.width() - self.MARGIN
            if self._open
            else parent_rect.width() + self.MARGIN
        )
        self.setGeometry(
            x,
            self.MARGIN,
            self.width(),
            max(240, parent_rect.height() - self.MARGIN * 2),
        )

    def eventFilter(self, watched, event) -> bool:
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            QTimer.singleShot(0, self.sync_geometry)
        return super().eventFilter(watched, event)
