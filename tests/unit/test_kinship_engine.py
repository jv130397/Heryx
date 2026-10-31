import pytest

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    KinshipEngine,
    KinshipSeverity,
    KinshipValidator,
    Parentage,
    ParentageKind,
    PedigreeProject,
    SiblingKind,
)


def family_with_parents():
    proband = Individual(label="P", gender_identity=GenderIdentity.UNKNOWN)
    project = PedigreeProject(individuals=[proband])
    project, parent_ids = FamilyService.add_parents(project, proband.id)
    return project, proband.id, parent_ids


def test_full_sibling_reuses_both_parents_without_creating_partnership() -> None:
    project, proband_id, parent_ids = family_with_parents()
    relation_count = len(project.relationships)
    plan = KinshipEngine().plan_sibling(project, proband_id, SiblingKind.FULL)
    updated = plan.apply()
    sibling_id = plan.created_ids[0]
    assert set(KinshipEngine.parents(updated, sibling_id)) == set(parent_ids)
    assert KinshipEngine().sibling_kind(updated, proband_id, sibling_id) == SiblingKind.FULL
    assert len(updated.relationships) == relation_count
    assert len(project.individuals) == 3  # planning never mutates the source


def test_paternal_half_sibling_has_distinct_mother_and_correct_classification() -> None:
    project, proband_id, parent_ids = family_with_parents()
    father_id = next(
        person_id
        for person_id in parent_ids
        if next(p for p in project.individuals if p.id == person_id).gender_identity
        == GenderIdentity.MAN
    )
    proband_mother = next(person_id for person_id in parent_ids if person_id != father_id)
    plan = KinshipEngine().plan_sibling(project, proband_id, SiblingKind.PATERNAL_HALF)
    updated = plan.apply()
    sibling_id = plan.created_ids[0]
    sibling_parents = set(KinshipEngine.parents(updated, sibling_id))
    assert father_id in sibling_parents
    assert proband_mother not in sibling_parents
    assert len(sibling_parents) == 2
    assert (
        KinshipEngine().sibling_kind(updated, proband_id, sibling_id) == SiblingKind.PATERNAL_HALF
    )


def test_maternal_half_sibling_can_reuse_explicit_different_father() -> None:
    project, proband_id, parent_ids = family_with_parents()
    mother_id = next(
        person_id
        for person_id in parent_ids
        if next(p for p in project.individuals if p.id == person_id).gender_identity
        == GenderIdentity.WOMAN
    )
    different_father = Individual(label="F2", gender_identity=GenderIdentity.MAN)
    project.individuals.append(different_father)
    plan = KinshipEngine().plan_sibling(
        project,
        proband_id,
        SiblingKind.MATERNAL_HALF,
        other_parent_id=different_father.id,
    )
    updated = plan.apply()
    sibling_id = plan.created_ids[0]
    assert set(KinshipEngine.parents(updated, sibling_id)) == {mother_id, different_father.id}
    assert (
        KinshipEngine().sibling_kind(updated, proband_id, sibling_id) == SiblingKind.MATERNAL_HALF
    )


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        (SiblingKind.UNRESOLVED, SiblingKind.UNRESOLVED),
        (SiblingKind.ADOPTIVE, SiblingKind.ADOPTIVE),
        (SiblingKind.SOCIAL, SiblingKind.SOCIAL),
    ],
)
def test_declared_siblings_do_not_invent_biological_parentage(kind, expected) -> None:
    proband = Individual()
    project = PedigreeProject(individuals=[proband])
    plan = KinshipEngine().plan_sibling(project, proband.id, kind)
    updated = plan.apply()
    sibling_id = plan.created_ids[0]
    assert updated.parentages == []
    assert KinshipEngine().sibling_kind(updated, proband.id, sibling_id) == expected


def test_half_sibling_rejects_same_other_parent() -> None:
    project, proband_id, parent_ids = family_with_parents()
    mother_id = next(
        person_id
        for person_id in parent_ids
        if next(p for p in project.individuals if p.id == person_id).gender_identity
        == GenderIdentity.WOMAN
    )
    with pytest.raises(ValueError, match="diferente"):
        KinshipEngine().plan_sibling(
            project,
            proband_id,
            SiblingKind.PATERNAL_HALF,
            other_parent_id=mother_id,
        )


def test_unknown_reconciliation_preserves_parentage_and_uuid_of_known_person() -> None:
    project, proband_id, _ = family_with_parents()
    plan = KinshipEngine().plan_sibling(project, proband_id, SiblingKind.PATERNAL_HALF)
    project = plan.apply()
    sibling_id = plan.created_ids[0]
    unknown_id = plan.unknown_ids[0]
    identified = Individual(label="M2", gender_identity=GenderIdentity.WOMAN)
    project.individuals.append(identified)
    reconciled = KinshipEngine().reconcile_unknown(project, unknown_id, identified.id).apply()
    assert unknown_id not in {person.id for person in reconciled.individuals}
    assert identified.id in set(KinshipEngine.parents(reconciled, sibling_id))


def test_validator_reports_duplicate_parentage_and_excess_biological_parents() -> None:
    child = Individual()
    parents = [Individual() for _ in range(3)]
    project = PedigreeProject(individuals=[child, *parents])
    project.parentages = [
        Parentage(parent_id=parents[0].id, child_id=child.id),
        Parentage(parent_id=parents[0].id, child_id=child.id),
        Parentage(parent_id=parents[1].id, child_id=child.id),
        Parentage(parent_id=parents[2].id, child_id=child.id),
    ]
    issues = KinshipValidator().validate(project)
    codes = {issue.code for issue in issues if issue.severity == KinshipSeverity.ERROR}
    assert {"duplicate_parentage", "too_many_biological_parents"} <= codes


def test_ancestors_and_descendants_return_shortest_generation_distance() -> None:
    root = Individual()
    project = PedigreeProject(individuals=[root])
    project, parents = FamilyService.add_parents(project, root.id)
    project, grandparents = FamilyService.add_parents(project, parents[0])
    engine = KinshipEngine()
    assert engine.ancestors(project, root.id)[grandparents[0]] == 2
    assert engine.descendants(project, grandparents[0])[root.id] == 2


def test_non_biological_parentage_does_not_define_biological_siblings() -> None:
    parent = Individual()
    first = Individual()
    second = Individual()
    project = PedigreeProject(
        individuals=[parent, first, second],
        parentages=[
            Parentage(parent_id=parent.id, child_id=first.id, kind=ParentageKind.SOCIAL),
            Parentage(parent_id=parent.id, child_id=second.id, kind=ParentageKind.SOCIAL),
        ],
    )
    assert KinshipEngine().sibling_kind(project, first.id, second.id) is None


def test_child_of_man_automatically_gets_unknown_biological_mother() -> None:
    father = Individual(label="F", gender_identity=GenderIdentity.MAN)
    project = PedigreeProject(individuals=[father])
    plan = KinshipEngine().plan_child(project, father.id)
    updated = plan.apply()
    child_id, mother_id = plan.created_ids
    mother = next(person for person in updated.individuals if person.id == mother_id)
    assert mother.placeholder
    assert mother.gender_identity == GenderIdentity.WOMAN
    assert mother_id in plan.unknown_ids
    assert set(KinshipEngine.parents(updated, child_id)) == {father.id, mother_id}
    assert updated.relationships == []

    from rarepedigree.layout import PedigreeLayoutEngine

    generations = PedigreeLayoutEngine().generations(updated)
    assert generations[mother_id] == generations[father.id]
    assert generations[child_id] == generations[father.id] + 1


def test_child_of_unspecified_parent_does_not_invent_coparent_sex() -> None:
    parent = Individual(gender_identity=GenderIdentity.UNKNOWN)
    project = PedigreeProject(individuals=[parent])
    plan = KinshipEngine().plan_child(project, parent.id)
    updated = plan.apply()
    unknown = next(person for person in updated.individuals if person.id == plan.unknown_ids[0])
    assert unknown.gender_identity == GenderIdentity.UNKNOWN


@pytest.mark.parametrize("size", [50, 100, 200])
def test_large_multinuclear_family_remains_valid_and_collision_free(size) -> None:
    father = Individual(label="F", gender_identity=GenderIdentity.MAN)
    people = [father]
    parentages = []
    for index in range((size - 1) // 2):
        mother = Individual(label=f"M{index}", gender_identity=GenderIdentity.WOMAN)
        child = Individual(label=f"C{index}")
        people.extend((mother, child))
        parentages.extend(
            (
                Parentage(parent_id=father.id, child_id=child.id),
                Parentage(parent_id=mother.id, child_id=child.id),
            )
        )
    if len(people) < size:
        people.append(Individual(label="Unrelated"))
    project = PedigreeProject(individuals=people, parentages=parentages)
    assert KinshipValidator().validate(project) == []

    from rarepedigree.layout import PedigreeLayoutEngine

    positions = PedigreeLayoutEngine().compute(project, preserve_locked=False)
    assert len(positions) == size
    assert len(set(positions.values())) == size
