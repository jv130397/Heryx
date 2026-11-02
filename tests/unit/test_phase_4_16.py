import json
from pathlib import Path

from PySide6.QtCore import QPoint, QSettings, Qt

from rarepedigree.domain import PedigreeProject
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.ui import MainWindow
from rarepedigree.ui.home import RecentProjectsStore, WelcomeScreen
from rarepedigree.ui.preferences import PreferencesDialog


def test_recent_projects_are_bounded_deduplicated_and_privacy_safe(tmp_path: Path) -> None:
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    store = RecentProjectsStore(settings)
    for index in range(RecentProjectsStore.MAX_ITEMS + 3):
        path = tmp_path / f"family-{index}.rps.json"
        path.touch()
        store.add(path, f"Family {index}")
    store.add(tmp_path / "family-5.rps.json", "Updated")
    projects = store.projects()
    assert len(projects) == RecentProjectsStore.MAX_ITEMS
    assert projects[0].title == "Updated"
    raw = json.loads(settings.value(RecentProjectsStore.KEY, "[]", str))
    assert set(raw[0]) == {"title", "path", "last_opened"}
    assert not any("individual" in entry for entry in raw)


def test_recent_project_removal_never_deletes_file(tmp_path: Path) -> None:
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    store = RecentProjectsStore(settings)
    project = tmp_path / "family.rps.json"
    project.write_text("{}")
    store.add(project)
    store.remove(project)
    assert project.exists()
    assert store.projects() == []


def test_welcome_actions_remain_available_during_animation(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    requested = []
    screen.newRequested.connect(lambda: requested.append("new"))
    screen.start_animation(reduced_motion=False)
    screen.new_card.button.click()
    assert requested == ["new"]
    assert screen.new_card.button.isEnabled()
    assert screen.illustration.progress < 1.0
    qtbot.keyClick(screen.new_card, Qt.Key.Key_Return)
    assert requested == ["new", "new"]


def test_reduced_motion_renders_final_welcome_state(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    screen.start_animation(reduced_motion=True)
    assert screen.illustration.progress == 1.0
    assert screen._animations.state() == screen._animations.State.Stopped
    assert screen._idle_animation.state() == screen._idle_animation.State.Stopped


def test_welcome_enters_gentle_idle_motion_after_reveal(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    screen.show()
    screen._start_idle_animation()
    assert screen._idle_animation.state() == screen._idle_animation.State.Running
    assert screen._idle_animation.duration() == 4200
    screen.stop_animation()
    assert screen.illustration.bobOffset == 0.0


def test_pointer_adds_bounded_parallax_and_card_icon_motion(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    screen.resize(1200, 700)
    screen.show()
    qtbot.mouseMove(screen.illustration, QPoint(screen.illustration.width() - 5, 5))
    qtbot.wait(260)
    assert 0.0 < screen.illustration.hoverX <= 6.0
    assert -5.0 <= screen.illustration.hoverY < 0.0
    qtbot.mouseMove(screen.new_card, QPoint(10, 10))
    qtbot.wait(200)
    assert screen.new_card.glyph.pixmap().width() >= 31


def test_reduced_motion_disables_pointer_animation(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    screen.start_animation(reduced_motion=True)
    screen.resize(1200, 700)
    screen.show()
    qtbot.mouseMove(screen.illustration, QPoint(screen.illustration.width() - 5, 5))
    qtbot.wait(260)
    assert screen.illustration.hoverX == 0.0
    assert screen.new_card.glyph.pixmap().width() == 28


def test_welcome_supports_light_and_midnight_theme_properties(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    screen.set_theme("light")
    assert screen.property("welcomeTheme") == "light"
    screen.set_theme("midnight")
    assert screen.property("welcomeTheme") == "midnight"


def test_welcome_theme_is_configurable_in_preferences(qtbot) -> None:
    dialog = PreferencesDialog()
    qtbot.addWidget(dialog)
    dialog.theme.setCurrentIndex(dialog.theme.findData("light"))
    dialog._save()
    assert QSettings().value("ui/welcome_theme") == "light"
    QSettings().setValue("ui/welcome_theme", "midnight")


def test_main_window_starts_on_home_and_can_enter_workspace(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.page_stack.currentWidget() is window.welcome_screen
    window.show_workspace()
    assert window.page_stack.currentWidget() is window.central_shell
    assert window.main_toolbar.isVisibleTo(window)
    assert window.show_home(force=True)
    assert window.page_stack.currentWidget() is window.welcome_screen


def test_loading_project_records_recent_and_enters_editor(qtbot, tmp_path: Path) -> None:
    settings = QSettings()
    settings.remove(RecentProjectsStore.KEY)
    project = PedigreeProject(title="Synthetic validation")
    path = tmp_path / "validation.rps.json"
    JsonProjectRepository().save(project, path)
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.load_from(path)
    assert window.page_stack.currentWidget() is window.central_shell
    assert window.recent_projects.projects()[0].path == path.resolve()


def test_unavailable_recent_project_is_retained_but_cannot_open(qtbot, tmp_path: Path) -> None:
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    store = RecentProjectsStore(settings)
    missing = tmp_path / "missing.rps.json"
    store.add(missing, "Missing")
    screen = WelcomeScreen(store)
    qtbot.addWidget(screen)
    screen.refresh_recent_projects()
    row = screen.recent_list.itemAt(0).widget()
    buttons = row.findChildren(type(screen.clear_recent_button))
    assert buttons and not buttons[0].isEnabled()
