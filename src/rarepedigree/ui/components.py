"""Reusable presentation components for the Scientific Workspace."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
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
