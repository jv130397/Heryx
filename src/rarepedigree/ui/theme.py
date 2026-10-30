# ruff: noqa: E501
"""Central visual tokens and QSS for RarePedigree Scientific Workspace."""

COLORS = {
    "background": "#0A0F1C",
    "panel": "#151E30",
    "surface": "#202D45",
    "accent": "#3B82F6",
    "violet": "#8B5CF6",
    "text": "#F8FAFC",
    "muted": "#A8B6CC",
    "canvas": "#F7F9FD",
    "border": "#2B3750",
    "danger": "#F43F5E",
}

SCIENTIFIC_WORKSPACE_STYLESHEET = """
* { font-family: "Inter", "Noto Sans", "Segoe UI", sans-serif; font-size: 14px; }
QMainWindow, QDialog { background: #0A0F1C; color: #F8FAFC; }
QMenuBar { background: #0A0F1C; color: #A8B6CC; padding: 2px 8px; }
QMenuBar::item { padding: 5px 9px; border-radius: 4px; }
QMenuBar::item:selected, QMenu::item:selected { background: #164E63; color: #F8FAFC; }
QMenu { background: #151E30; color: #F8FAFC; border: 1px solid #2B3750; padding: 7px; }
QMenu::item { padding: 7px 28px 7px 10px; border-radius: 4px; }
QToolBar { background: #10192B; border: 0; border-bottom: 1px solid #2B3750; spacing: 5px; padding: 7px 12px; }
QToolBar::separator { background: #334155; width: 1px; margin: 5px 8px; }
QToolButton { color: #E2E8F0; background: transparent; border: 1px solid transparent; border-radius: 6px; padding: 6px; }
QToolButton:hover { background: #1E3A4F; border-color: #475569; }
QToolButton:focus { border: 2px solid #22D3EE; }
QToolButton:pressed, QToolButton:checked { background: #1D4ED8; border-color: #22D3EE; }
QToolButton[railButton="true"] { min-width: 42px; min-height: 42px; }
QDockWidget { color: #F8FAFC; }
QDockWidget::title { background: #151E30; padding: 11px 14px; border-bottom: 1px solid #2B3750; font-weight: 600; }
QDockWidget QWidget { background: #151E30; color: #E2E8F0; }
QTabWidget::pane { border: 0; background: #172338; }
QTabBar::tab { background: transparent; color: #94A3B8; padding: 9px 12px; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #F8FAFC; border-bottom-color: #22D3EE; }
QPushButton { background: #1E293B; color: #F8FAFC; border: 1px solid #475569; border-radius: 6px; padding: 7px 12px; }
QPushButton:hover { background: #26364D; border-color: #22D3EE; }
QPushButton:focus { border: 2px solid #22D3EE; }
QPushButton:disabled { color: #64748B; background: #172033; border-color: #334155; }
QPushButton#primary-button { background: #3B82F6; border-color: #60A5FA; font-weight: 600; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #0F1A2C; color: #F8FAFC; border: 1px solid #475569; border-radius: 5px; padding: 7px; min-height: 18px; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #22D3EE; }
QLineEdit:disabled { color: #94A3B8; background: #172338; }
QCheckBox { color: #E2E8F0; spacing: 8px; min-height: 26px; }
QLabel { color: #E2E8F0; background: transparent; }
QLabel[sectionHeader="true"] { color: #67E8F9; font-size: 11px; font-weight: 700; padding-top: 8px; }
QStatusBar { background: #0B1220; color: #94A3B8; border-top: 1px solid #334155; }
QStatusBar::item { border: 0; }
QGraphicsView { border: 0; background: #F8FAFC; }
QScrollBar { background: transparent; width: 9px; height: 9px; }
QScrollBar::handle { background: #94A3B8; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QFrame#tool-rail { background: #151E30; border: 1px solid #2B3750; border-radius: 10px; }
QFrame#properties-drawer { background: #151E30; border-left: 1px solid #30415F; }
QFrame#empty-state { background: rgba(255,255,255,235); border: 1px solid #CBD5E1; border-radius: 12px; }
QFrame#empty-state QLabel { color: #475569; }
QLabel#empty-title { color: #0F172A; font-size: 18px; font-weight: 700; }
QLabel#empty-mark { color: #0891B2; font-size: 38px; }
QWidget#zoom-control { background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 7px; }
QWidget#zoom-control QLabel, QWidget#zoom-control QToolButton { color: #334155; background: transparent; }
QPushButton[symbolCard="true"] { font-size: 28px; min-width: 62px; min-height: 52px; }
QPushButton[symbolCard="true"]:checked { background: #1D4ED8; border: 2px solid #22D3EE; }
QDialog#welcome-dialog { background: #10192B; }
QLabel#welcome-title { font-size: 22px; font-weight: 700; }
QLabel#welcome-mark { color: #8B5CF6; font-size: 48px; }
QFrame#toast { background: #202D45; color: #F8FAFC; border: 1px solid #3B82F6; border-radius: 9px; }
QFrame#toast QLabel { padding: 5px; }
QFrame#toast[level="warning"] { border-color: #F59E0B; }
QFrame#toast[level="error"] { border-color: #F43F5E; }
"""
