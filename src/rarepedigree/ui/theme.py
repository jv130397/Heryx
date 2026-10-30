SCIENTIFIC_WORKSPACE_STYLESHEET = """
QMainWindow, QDialog { background: #101923; color: #e7f2f8; }
QMenuBar, QMenu, QToolBar, QDockWidget { background: #152331; color: #e7f2f8; }
QMenuBar::item:selected, QMenu::item:selected { background: #187b9b; }
QToolBar { border: 0; spacing: 6px; padding: 6px; }
QToolButton { color: #e7f2f8; background: transparent; border: 1px solid transparent;
              border-radius: 4px; padding: 5px; }
QToolButton:hover, QToolButton:focus { background: #24485d; border-color: #35c5e8; }
QDockWidget::title { padding: 8px; background: #1a2d3d; }
QDockWidget QWidget { background: #152331; color: #dcecf3; }
QTabWidget::pane { border: 1px solid #31566d; background: #152331; }
QTabBar::tab { background: #1d3445; color: #dcecf3; padding: 7px; }
QTabBar::tab:selected { background: #187b9b; color: white; }
QPushButton { background: #1d3445; color: #eef8fb; border: 1px solid #31566d;
              border-radius: 5px; padding: 8px; text-align: left; }
QPushButton:hover, QPushButton:focus { border-color: #35c5e8; background: #24485d; }
QPushButton:pressed { background: #126b89; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #f7fbfd; color: #152331;
              border: 1px solid #668696; border-radius: 4px; padding: 5px; }
QCheckBox, QLabel { color: #dcecf3; }
QStatusBar { background: #0d151d; color: #9fc4d4; }
QGraphicsView { border: 1px solid #31566d; background: #f7f9fb; }
"""
