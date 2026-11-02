from PySide6.QtCore import QPoint, QSettings, Qt

from rarepedigree.ui import MainWindow
from rarepedigree.ui.genomic_sphere import GenomicSphere, SphereParameters


def test_sphere_geometry_is_deterministic_and_bounded(qtbot) -> None:
    first = GenomicSphere()
    second = GenomicSphere()
    qtbot.addWidget(first)
    qtbot.addWidget(second)
    assert first._vertices == second._vertices
    assert first._edges == second._edges
    assert len(first._vertices) == 74
    assert all(0 <= left < right < 74 for left, right in first._edges)


def test_sphere_parameters_are_clamped_and_loaded_from_settings(tmp_path) -> None:
    settings = QSettings(str(tmp_path / "sphere.ini"), QSettings.Format.IniFormat)
    settings.setValue("welcome/sphere_fps", 500)
    settings.setValue("welcome/sphere_deformation", 0.11)
    parameters = SphereParameters.from_settings(settings)
    assert parameters.fps_limit == 60
    assert parameters.deformation == 0.11


def test_sphere_stops_when_hidden_and_restarts_when_shown(qtbot) -> None:
    sphere = GenomicSphere()
    qtbot.addWidget(sphere)
    sphere.resize(500, 500)
    sphere.show()
    sphere.start()
    assert sphere.timer_active
    sphere.hide()
    assert not sphere.timer_active
    sphere.show()
    assert sphere.timer_active


def test_reduced_motion_is_static_and_ignores_pointer(qtbot) -> None:
    sphere = GenomicSphere()
    qtbot.addWidget(sphere)
    sphere.resize(500, 500)
    sphere.show()
    sphere.start(reduced_motion=True)
    before = sphere._projected()
    qtbot.mouseMove(sphere, QPoint(490, 10))
    qtbot.wait(40)
    after = sphere._projected()
    assert not sphere.timer_active
    assert before == after
    assert sphere.hoverX == 0.0


def test_drag_rotates_sphere_and_click_emits_pulse(qtbot) -> None:
    sphere = GenomicSphere()
    qtbot.addWidget(sphere)
    sphere.resize(500, 500)
    sphere.show()
    sphere.start()
    events: list[str] = []
    sphere.interactionChanged.connect(events.append)
    qtbot.mousePress(sphere, Qt.MouseButton.LeftButton, pos=QPoint(220, 220))
    qtbot.mouseMove(sphere, QPoint(310, 250))
    qtbot.mouseRelease(sphere, Qt.MouseButton.LeftButton, pos=QPoint(310, 250))
    assert "drag" in events
    assert sphere._inertia_x or sphere._inertia_y
    qtbot.mouseClick(sphere, Qt.MouseButton.LeftButton, pos=QPoint(250, 250))
    assert "pulse" in events
    assert sphere._pulse == 1.0


def test_projection_remains_inside_responsive_widget(qtbot) -> None:
    sphere = GenomicSphere()
    qtbot.addWidget(sphere)
    for width, height in ((360, 300), (700, 360), (520, 680)):
        sphere.resize(width, height)
        points = [point for point, _z, _perspective in sphere._projected()]
        assert points
        assert all(0 <= point.x() <= width and 0 <= point.y() <= height for point in points)


def test_main_window_hides_native_menu_on_home_and_stops_sphere_in_editor(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1366, 768)
    window.show()
    assert not window.menuBar().isVisible()
    assert window.welcome_screen.sphere.timer_active
    window.show_workspace()
    assert window.menuBar().isVisible()
    assert not window.welcome_screen.sphere.timer_active

