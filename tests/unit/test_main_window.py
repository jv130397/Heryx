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


def test_contextual_parents_are_atomic_and_undoable(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.UNKNOWN)
    window.undo_stack.setClean()
    window._context_action(window.scene.person_items[person.id], "parents")
    assert len(window.project.individuals) == 3
    assert len(window.project.parentages) == 2
    assert len(window.scene.parentage_items) == 1
    window.undo_stack.undo()
    assert len(window.project.individuals) == 1
    window.undo_stack.redo()
    assert len(window.project.individuals) == 3


def test_contextual_delete_removes_edges_and_is_undoable(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.MAN)
    window._context_action(window.scene.person_items[person.id], "partner")
    assert len(window.project.relationships) == 1
    window._context_action(window.scene.person_items[person.id], "delete")
    assert person.id not in {item.id for item in window.project.individuals}
    assert window.project.relationships == []
    window.undo_stack.undo()
    assert person.id in {item.id for item in window.project.individuals}
    assert len(window.project.relationships) == 1
