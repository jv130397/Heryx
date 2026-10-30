import pytest

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    ParentageKind,
    PedigreeProject,
    Relationship,
)
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


def test_partners_are_kept_in_the_same_generation() -> None:
    child = Individual(label="II-1")
    project = PedigreeProject(individuals=[child])
    project, _ = FamilyService.add_parents(project, child.id)
    partner = Individual(label="II-2")
    project.individuals.append(partner)
    project.relationships.append(Relationship(member_a=child.id, member_b=partner.id))
    generations = PedigreeLayoutEngine().generations(project)
    assert generations[child.id] == generations[partner.id] == 1
    _assert_no_position_collisions(project)


def _assert_no_position_collisions(project: PedigreeProject) -> None:
    positions = PedigreeLayoutEngine().compute(project, preserve_locked=False)
    assert len(set(positions.values())) == len(project.individuals)


@pytest.mark.parametrize("gender", [GenderIdentity.MAN, GenderIdentity.WOMAN])
def test_single_new_parent_is_above_child_without_collision(gender) -> None:
    child = Individual()
    project = PedigreeProject(individuals=[child])
    project, parent_id = FamilyService.add_parent(project, child.id, gender)
    engine = PedigreeLayoutEngine()
    generations = engine.generations(project)
    assert generations[parent_id] + 1 == generations[child.id]
    _assert_no_position_collisions(project)


@pytest.mark.parametrize("unknown", [False, True])
def test_parent_pair_is_above_child_without_collision(unknown) -> None:
    child = Individual()
    project = PedigreeProject(individuals=[child])
    project, parent_ids = FamilyService.add_parents(project, child.id, unknown=unknown)
    engine = PedigreeLayoutEngine()
    generations = engine.generations(project)
    assert all(generations[parent_id] + 1 == generations[child.id] for parent_id in parent_ids)
    _assert_no_position_collisions(project)


@pytest.mark.parametrize("kind", [ParentageKind.BIOLOGICAL, ParentageKind.LEGAL])
def test_new_child_is_below_parent_without_collision(kind) -> None:
    parent = Individual()
    project = PedigreeProject(individuals=[parent])
    project, child_id = FamilyService.add_child(project, parent.id, kind=kind)
    generations = PedigreeLayoutEngine().generations(project)
    assert generations[child_id] == generations[parent.id] + 1
    _assert_no_position_collisions(project)


def test_new_sibling_shares_generation_without_collision() -> None:
    person = Individual()
    project = PedigreeProject(individuals=[person])
    project, sibling_id = FamilyService.add_sibling(project, person.id)
    generations = PedigreeLayoutEngine().generations(project)
    assert generations[sibling_id] == generations[person.id]
    _assert_no_position_collisions(project)
