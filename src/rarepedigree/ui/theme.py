# ruff: noqa: E501
"""Model-driven Genomic Nexus visual tokens and Qt stylesheet."""

COLORS = {
    "workspace": "#E9ECEF",
    "canvas": "#F1F3F5",
    "surface": "#FFFFFF",
    "surface_alt": "#F7F9FA",
    "header": "#1C293B",
    "header_hover": "#26384F",
    "accent": "#078FC2",
    "accent_hover": "#087EAA",
    "accent_soft": "#E8F6FA",
    "text": "#1F2933",
    "muted": "#66737F",
    "border": "#D6DCE1",
    "border_strong": "#B8C2CB",
    "success": "#238A63",
    "warning": "#D58B16",
    "danger": "#C93C55",
}

SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24}
RADII = {"control": 5, "card": 8, "overlay": 11}
MOTION = {"fast": 120, "panel": 180, "toast": 200}
TYPOGRAPHY = {
    "caption": 11,
    "label": 12,
    "body": 14,
    "section": 15,
    "dialog_title": 17,
    "window_title": 20,
}
ICONS = {"compact": 18, "default": 20, "brand": 30}
CONTROLS = {"height": 36, "target": 44, "rail_compact": 60, "rail_expanded": 210}
ELEVATION = {
    "popover": (0, 6, 18, 45),
    "drawer": (-5, 6, 28, 85),
    "dialog": (0, 10, 32, 80),
}
BREAKPOINTS = {"compact": 1366, "desktop": 1920, "large": 2560}

SCIENTIFIC_WORKSPACE_STYLESHEET = """
* { font-family: "Inter", "Noto Sans", "Segoe UI", sans-serif; font-size: 14px; }
QMainWindow { background: #E9ECEF; color: #1F2933; }
QDialog, QWizard, QMessageBox { background: #FFFFFF; color: #1F2933; }
QMenuBar { background: #FFFFFF; color: #334155; padding: 2px 10px; border-bottom: 1px solid #D6DCE1; }
QMenuBar::item { padding: 5px 9px; border-radius: 4px; }
QMenuBar::item:selected { background: #E8F6FA; color: #075E7D; }
QMenu { background: #FFFFFF; color: #1F2933; border: 1px solid #C9D1D8; padding: 6px; }
QMenu::separator { height: 1px; background: #E2E7EB; margin: 5px 8px; }
QMenu::item { padding: 7px 30px 7px 10px; border-radius: 4px; }
QMenu::item:selected { background: #E8F6FA; color: #075E7D; }
QMenu::item:disabled { color: #A4ADB5; }
QToolBar { background: #FFFFFF; border: 0; border-bottom: 1px solid #D6DCE1; spacing: 3px; padding: 5px 10px; }
QToolBar::separator { background: #D6DCE1; width: 1px; margin: 5px 8px; }
QToolButton { color: #334155; background: transparent; border: 1px solid transparent; border-radius: 5px; padding: 6px; }
QToolButton:hover { background: #E8F6FA; border-color: #B8DCE8; color: #075E7D; }
QToolButton:focus { border: 2px solid #078FC2; }
QToolButton:pressed, QToolButton:checked { background: #D9F0F7; border-color: #078FC2; color: #075E7D; }
QToolButton:disabled { color: #A4ADB5; }
QToolButton[railButton="true"] { min-width: 38px; min-height: 38px; }
QTabWidget::pane { border: 0; background: #FFFFFF; }
QTabBar::tab { background: transparent; color: #66737F; padding: 9px 12px; border-bottom: 2px solid transparent; }
QTabBar::tab:hover { color: #075E7D; background: #F5FAFC; }
QTabBar::tab:selected { color: #075E7D; border-bottom-color: #078FC2; font-weight: 600; }
QPushButton { background: #FFFFFF; color: #1F2933; border: 1px solid #BFC8D0; border-radius: 5px; padding: 7px 12px; min-height: 20px; }
QPushButton:hover { background: #F3FAFC; border-color: #078FC2; color: #075E7D; }
QPushButton:focus { border: 2px solid #078FC2; }
QPushButton:pressed { background: #D9F0F7; }
QPushButton:disabled { color: #A4ADB5; background: #F4F5F6; border-color: #D6DCE1; }
QPushButton#primary-button, QDialogButtonBox QPushButton[text="Salvar"], QDialogButtonBox QPushButton[text="Save"] { background: #078FC2; color: #FFFFFF; border-color: #078FC2; font-weight: 600; }
QPushButton#primary-button:hover { background: #087EAA; }
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #FFFFFF; color: #1F2933; border: 1px solid #BFC8D0; border-radius: 5px; padding: 6px 8px; min-height: 20px; selection-background-color: #BFE7F2; }
QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover { border-color: #8FA0AD; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #078FC2; }
QLineEdit:disabled, QComboBox:disabled { color: #8B969F; background: #F1F3F5; }
QComboBox::drop-down { border: 0; width: 24px; }
QComboBox QAbstractItemView { background: #FFFFFF; color: #1F2933; border: 1px solid #BFC8D0; selection-background-color: #D9F0F7; selection-color: #075E7D; padding: 4px; }
QCheckBox, QRadioButton { color: #334155; spacing: 9px; min-height: 26px; }
QCheckBox::indicator, QRadioButton::indicator {
    width: 17px;
    height: 17px;
    background: #FFFFFF;
    border: 2px solid #8795A1;
}
QCheckBox::indicator { border-radius: 4px; }
QRadioButton::indicator { border-radius: 10px; }
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #078FC2;
    background: #F3FAFC;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: #078FC2;
    border-color: #075E7D;
}
QCheckBox::indicator:checked:hover, QRadioButton::indicator:checked:hover {
    background: #087EAA;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    background: #E9EDF0;
    border-color: #BFC8D0;
}
QCheckBox:focus, QRadioButton:focus {
    color: #075E7D;
}
QDialog QTabWidget::pane, QDialog QScrollArea, QDialog QScrollArea QWidget#qt_scrollarea_viewport {
    background: #FFFFFF;
}
QDialog QScrollArea > QWidget > QWidget { background: #FFFFFF; }
QLabel { color: #334155; background: transparent; }
QLabel[sectionHeader="true"] { color: #075E7D; font-size: 11px; font-weight: 700; padding-top: 6px; letter-spacing: 0.5px; }
QLabel[card="true"] { background: #F7F9FA; border: 1px solid #D6DCE1; border-radius: 7px; padding: 10px; }
QStatusBar { background: #FFFFFF; color: #66737F; border-top: 1px solid #D6DCE1; min-height: 25px; }
QStatusBar::item { border: 0; }
QGraphicsView { border: 0; background: #F1F3F5; }
QScrollBar { background: transparent; width: 9px; height: 9px; }
QScrollBar::handle { background: #B8C2CB; border-radius: 4px; min-height: 28px; }
QScrollBar::handle:hover { background: #8D9AA5; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QFrame#tool-rail { background: #FFFFFF; border: 1px solid #D6DCE1; border-radius: 9px; }
QFrame#rail-separator { color: #D6DCE1; background: #D6DCE1; max-height: 1px; margin: 5px 7px; }
QFrame#properties-drawer { background: #FFFFFF; border: 1px solid #C9D1D8; border-radius: 10px; }
QFrame#nexus-dialog-header { background: #1C293B; border-top-left-radius: 8px; border-top-right-radius: 8px; }
QFrame#nexus-dialog-header QLabel#nexus-dialog-title { color: #FFFFFF; font-size: 16px; font-weight: 700; }
QFrame#nexus-dialog-header QLabel#nexus-dialog-subtitle { color: #C8D2DC; font-size: 12px; }
QWidget#drawer-header { background: #1C293B; border-top-left-radius: 9px; border-top-right-radius: 9px; }
QWidget#drawer-header QLabel, QWidget#drawer-header QToolButton { color: #FFFFFF; }
QFrame#empty-state { background: rgba(255,255,255,242); border: 1px solid #D6DCE1; border-radius: 10px; }
QFrame#empty-state QLabel { color: #66737F; }
QLabel#empty-title { color: #1F2933; font-size: 19px; font-weight: 700; }
QLabel#empty-mark { color: #078FC2; font-size: 38px; }
QWidget#zoom-control { background: #FFFFFF; border: 1px solid #C9D1D8; border-radius: 10px; }
QWidget#zoom-control QLabel, QWidget#zoom-control QToolButton { color: #334155; background: transparent; }
QWidget#view-mode-control { background: #F7F9FA; border: 1px solid #D6DCE1; border-radius: 6px; }
QFrame#individual-search { background: #FFFFFF; border: 1px solid #C9D1D8; border-radius: 10px; }
QFrame#individual-search QListWidget { background: #FFFFFF; color: #1F2933; border: 1px solid #D6DCE1; border-radius: 6px; }
QFrame#individual-search QListWidget::item { padding: 8px; border-radius: 4px; }
QFrame#individual-search QListWidget::item:selected { background: #D9F0F7; color: #075E7D; }
QPushButton[symbolCard="true"] { font-size: 28px; min-width: 62px; min-height: 52px; }
QPushButton[symbolCard="true"]:checked { background: #D9F0F7; border: 2px solid #078FC2; color: #075E7D; }
QDialog#welcome-dialog { background: #FFFFFF; }
QLabel#welcome-title { font-size: 22px; font-weight: 700; color: #1F2933; }
QLabel#welcome-mark { color: #078FC2; font-size: 48px; }
QWidget#welcome-screen { background: #0C1427; }
QFrame#welcome-utility { background: #0A1323; border-bottom: 1px solid #223451; min-height: 34px; }
QLabel#welcome-utility-brand { color: #AFC1D8; font-size: 11px; font-weight: 650; }
QFrame#welcome-utility QToolButton { color: #C9D7E8; min-width: 28px; min-height: 24px; padding: 2px 6px; }
QFrame#welcome-hero { background: #0C1427; border: 0; }
QFrame#welcome-actions { background: #111B31; border-left: 1px solid #263755; }
QLabel#welcome-brand { color: #F2F8FF; font-size: 24px; font-weight: 750; }
QLabel#welcome-tagline { color: #78D9F6; font-size: 14px; letter-spacing: 1px; }
QLabel#welcome-hero-heading { color: #F2F6FB; font-size: 25px; font-weight: 720; padding-top: 18px; }
QLabel#welcome-hero-description { color: #A8B7CC; font-size: 13px; }
QWidget#genomic-sphere { background: transparent; }
QLabel#welcome-privacy { color: #8FA3C2; font-size: 12px; }
QLabel#welcome-heading { color: #F4F7FD; font-size: 26px; font-weight: 750; }
QLabel#welcome-intro { color: #AAB8CE; font-size: 14px; padding-bottom: 5px; }
QFrame#welcome-action-card { background: #17243E; border: 1px solid #2A3D60; border-radius: 10px; }
QFrame#welcome-action-card:hover { background: #1C2D4C; border-color: #4BBDE8; }
QLabel#welcome-card-icon { background: #10213D; border: 1px solid #29486B; border-radius: 9px; }
QLabel#welcome-card-title { color: #F3F7FC; font-size: 15px; font-weight: 700; }
QLabel#welcome-card-description { color: #AAB8CE; font-size: 12px; }
QPushButton#welcome-card-hit-target { min-width: 34px; min-height: 34px; max-width: 34px; padding: 0; background: transparent; border-color: #3B5275; }
QPushButton#welcome-card-hit-target:hover, QPushButton#welcome-card-hit-target:focus { background: #263E62; border-color: #62D4FF; }
QFrame#recent-projects-panel { background: #0E192D; border: 1px solid #293B5B; border-radius: 8px; }
QFrame#recent-project-row { background: #15223A; border-radius: 6px; }
QFrame#recent-project-row[unavailable="true"] { background: #171E2B; }
QLabel#recent-project-title { color: #E6EDF8; font-size: 12px; font-weight: 650; }
QLabel#recent-project-path, QLabel#recent-empty { color: #8294AF; font-size: 10px; }
QFrame#recent-projects-panel QPushButton, QFrame#recent-projects-panel QToolButton { color: #D7E3F3; background: #172B49; border-color: #355173; }
QWidget#welcome-screen[welcomeTheme="light"] { background: #F3F7FA; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#welcome-utility { background: #FFFFFF; border-bottom-color: #D8E3E9; }
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-utility-brand,
QWidget#welcome-screen[welcomeTheme="light"] QFrame#welcome-utility QToolButton { color: #536575; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#welcome-hero { background: #EAF3F8; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#welcome-actions { background: #FFFFFF; border-left-color: #D6E2E8; }
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-brand,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-heading,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-hero-heading { color: #17283B; }
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-tagline { color: #087EAA; }
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-privacy,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-intro,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-hero-description,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-card-description { color: #647586; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#welcome-action-card { background: #F8FBFC; border-color: #CAD9E1; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#welcome-action-card:hover { background: #EFF8FB; border-color: #078FC2; }
QWidget#welcome-screen[welcomeTheme="light"] QLabel#welcome-card-title,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#recent-project-title { color: #203244; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#recent-projects-panel { background: #F3F7F9; border-color: #CAD9E1; }
QWidget#welcome-screen[welcomeTheme="light"] QFrame#recent-project-row { background: #FFFFFF; }
QWidget#welcome-screen[welcomeTheme="light"] QLabel#recent-project-path,
QWidget#welcome-screen[welcomeTheme="light"] QLabel#recent-empty { color: #687987; }
QFrame#toast { background: #1C293B; color: #FFFFFF; border: 1px solid #2D425B; border-radius: 9px; }
QFrame#toast QLabel { color: #FFFFFF; padding: 5px; }
QFrame#toast[level="warning"] { border-color: #D58B16; }
QFrame#toast[level="error"] { border-color: #C93C55; }
QFrame#context-family-bar { background: #FFFFFF; border: 1px solid #BFC8D0; border-radius: 9px; }
QFrame#context-family-bar QLabel#context-person-label { color: #17233B; font-weight: 700; padding-left: 4px; }
QToolButton[connectionPoint="true"] { min-width: 38px; min-height: 38px; border: 2px solid #38BDF8; border-radius: 20px; color: #17233B; font-size: 17px; background: #F7FAFF; }
QToolButton[connectionPoint="true"]:hover { background: #E8F6FA; border-color: #8B5CF6; }
QFrame#floating-individual-editor { background: #FFFFFF; border: 1px solid #BFC8D0; border-radius: 10px; }
QFrame#floating-editor-header { background: #17233B; border-top-left-radius: 9px; border-top-right-radius: 9px; }
QFrame#floating-editor-header QLabel, QFrame#floating-editor-header QToolButton { color: #FFFFFF; font-weight: 700; }
QWizard { background: #FFFFFF; }
QWizardPage { background: #FFFFFF; }
QTableView, QTableWidget { background: #FFFFFF; alternate-background-color: #F7F9FA; color: #1F2933; gridline-color: #E2E7EB; border: 1px solid #D6DCE1; }
QHeaderView::section { background: #F1F3F5; color: #334155; border: 0; border-bottom: 1px solid #D6DCE1; padding: 7px; font-weight: 600; }
"""
