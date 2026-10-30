import pytest
from pydantic import ValidationError

from rarepedigree.domain import (
    FamilyService,
    Individual,
    Parentage,
    PedigreeProject,
    TwinZygosity,
)


def test_contextual_family_builds_three_generations_and_preserves_integrity() -> None:
    root = Individual(label="II-1")
    project = PedigreeProject(individuals=[root])
    project, parents = FamilyService.add_parents(project, root.id)
    project, child_id = FamilyService.add_child(project, root.id)
    project, sibling_id = FamilyService.add_sibling(project, root.id)
    assert len(project.individuals) == 5
    assert len(project.parentages) == 5
    assert {edge.parent_id for edge in project.parentages if edge.child_id == sibling_id} == set(
        parents
    )
    assert any(
        edge.child_id == child_id and edge.parent_id == root.id
        for edge in project.parentages
    )


def test_parentage_cycle_is_rejected() -> None:
    first = Individual()
    second = Individual()
    with pytest.raises(ValidationError, match="cycle"):
        PedigreeProject(
            individuals=[first, second],
            parentages=[
                Parentage(parent_id=first.id, child_id=second.id),
                Parentage(parent_id=second.id, child_id=first.id),
            ],
        )


def test_delete_removes_dependent_edges() -> None:
    root = Individual()
    project = PedigreeProject(individuals=[root])
    project, child_id = FamilyService.add_child(project, root.id)
    project = FamilyService.delete_individual(project, root.id)
    assert [person.id for person in project.individuals] == [child_id]
    assert project.parentages == []


def test_twins_require_shared_recorded_parents() -> None:
    root = Individual()
    project = PedigreeProject(individuals=[root])
    project, first = FamilyService.add_sibling(project, root.id)
    project = FamilyService.set_twins(project, [root.id, first], TwinZygosity.MONOZYGOTIC)
    assert project.twin_groups[0].member_ids == [root.id, first]
