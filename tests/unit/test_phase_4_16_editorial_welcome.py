from PySide6.QtCore import QPoint

from rarepedigree.ui.home import WelcomeScreen
from rarepedigree.ui.living_pedigree import LivingPedigree


def test_living_pedigree_uses_clinical_symbols_and_generations(qtbot) -> None:
    pedigree = LivingPedigree()
    qtbot.addWidget(pedigree)
    assert len(pedigree.people) == 9
    assert {person.shape for person in pedigree.people} == {"square", "circle", "diamond"}
    assert sum(person.proband for person in pedigree.people) == 1
    assert any(person.affected for person in pedigree.people)


def test_living_pedigree_hover_exposes_context_without_moving_layout(qtbot) -> None:
    pedigree = LivingPedigree()
    qtbot.addWidget(pedigree)
    pedigree.resize(720, 470)
    pedigree.show()
    target = pedigree._point(pedigree.people[7]).toPoint()
    before = pedigree._point(pedigree.people[7])
    qtbot.mouseMove(pedigree, target)
    assert pedigree._hovered == 7
    assert pedigree.people[pedigree._hovered].detail.startswith("Probando")
    assert pedigree._point(pedigree.people[7]) == before


def test_living_pedigree_reduced_motion_is_static(qtbot) -> None:
    pedigree = LivingPedigree()
    qtbot.addWidget(pedigree)
    pedigree.show()
    pedigree.start(reduced_motion=True)
    qtbot.mouseMove(pedigree, QPoint(pedigree.width() - 2, 2))
    assert not pedigree.timer_active
    assert pedigree.hoverX == 0.0
    assert pedigree.hoverY == 0.0


def test_recent_projects_is_visually_secondary(qtbot) -> None:
    screen = WelcomeScreen()
    qtbot.addWidget(screen)
    assert screen.recent_card.property("secondaryAction") is True
    assert screen.recent_card.minimumHeight() < screen.new_card.minimumHeight()

