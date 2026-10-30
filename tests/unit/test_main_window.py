from rarepedigree.domain import GenderIdentity
from rarepedigree.ui import MainWindow


def test_add_person_supports_undo_and_redo(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    assert person in window.project.individuals
    assert person.id in window.scene.person_items

    window.undo_stack.undo()
    assert person not in window.project.individuals
    assert person.id not in window.scene.person_items

    window.undo_stack.redo()
    assert person in window.project.individuals
    assert person.id in window.scene.person_items
