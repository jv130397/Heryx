from rarepedigree.domain import FamilyService, Individual, PedigreeProject
from rarepedigree.layout import PedigreeLayoutEngine


def test_layout_distributes_three_generations() -> None:
    root = Individual()
    project = PedigreeProject(individuals=[root])
    project, parents = FamilyService.add_parents(project, root.id)
    project, grandparents = FamilyService.add_parents(project, parents[0])
    engine = PedigreeLayoutEngine()
    generation = engine.generations(project)
    positions = engine.compute(project, preserve_locked=False)
    assert generation[grandparents[0]] == 0
    assert generation[parents[0]] == 1
    assert generation[root.id] == 2
    assert positions[root.id][1] > positions[parents[0]][1] > positions[grandparents[0]][1]


def test_layout_preserves_locked_manual_position() -> None:
    person = Individual()
    person.layout.x = 321
    person.layout.y = 654
    person.layout.locked = True
    positions = PedigreeLayoutEngine().compute(PedigreeProject(individuals=[person]))
    assert positions[person.id] == (321, 654)
