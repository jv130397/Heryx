from rarepedigree.domain import (
    GenderIdentity,
    Individual,
    KinshipEngine,
    PedigreeProject,
    SiblingKind,
)


def test_maternal_grandfather_can_be_added_before_mother() -> None:
    proband = Individual(label="P")
    project = PedigreeProject(individuals=[proband])
    plan = KinshipEngine().plan_ancestor_path(
        project,
        proband.id,
        [GenderIdentity.WOMAN, GenderIdentity.MAN],
        label="GF-M",
    )
    updated = plan.apply()
    mother_id = KinshipEngine.parents(updated, proband.id)[0]
    grandfather_id = KinshipEngine.parents(updated, mother_id)[0]
    mother = next(person for person in updated.individuals if person.id == mother_id)
    grandfather = next(person for person in updated.individuals if person.id == grandfather_id)
    assert mother.placeholder
    assert mother.id in plan.unknown_ids
    assert grandfather.label == "GF-M"
    assert grandfather.gender_identity == GenderIdentity.MAN


def test_bisancestor_path_reuses_existing_intermediate() -> None:
    proband = Individual()
    project = PedigreeProject(individuals=[proband])
    first = KinshipEngine().plan_ancestor_path(project, proband.id, [GenderIdentity.MAN], label="F")
    project = first.apply()
    plan = KinshipEngine().plan_ancestor_path(
        project,
        proband.id,
        [GenderIdentity.MAN, GenderIdentity.WOMAN, GenderIdentity.MAN],
        label="GGF",
    )
    assert first.created_ids[0] in plan.reused_ids
    assert len(plan.created_ids) == 2


def test_maternal_aunt_uses_maternal_branch() -> None:
    proband = Individual()
    project = PedigreeProject(individuals=[proband])
    plan = KinshipEngine().plan_aunt_uncle(
        project,
        proband.id,
        branch_gender=GenderIdentity.WOMAN,
        relative_gender=GenderIdentity.WOMAN,
        label="Aunt-M",
    )
    updated = plan.apply()
    mother_id = next(
        parent_id
        for parent_id in KinshipEngine.parents(updated, proband.id)
        if next(p for p in updated.individuals if p.id == parent_id).gender_identity
        == GenderIdentity.WOMAN
    )
    aunt = next(person for person in updated.individuals if person.label == "Aunt-M")
    assert KinshipEngine().sibling_kind(updated, mother_id, aunt.id) == SiblingKind.FULL


def test_paternal_half_uncle_shares_only_grandfather() -> None:
    proband = Individual()
    project = PedigreeProject(individuals=[proband])
    father_plan = KinshipEngine().plan_ancestor_path(
        project, proband.id, [GenderIdentity.MAN], label="Father"
    )
    project = father_plan.apply()
    father_id = father_plan.created_ids[0]
    project = (
        KinshipEngine()
        .plan_ancestor_path(project, father_id, [GenderIdentity.MAN], label="Grandfather")
        .apply()
    )
    plan = KinshipEngine().plan_aunt_uncle(
        project,
        proband.id,
        branch_gender=GenderIdentity.MAN,
        relative_gender=GenderIdentity.MAN,
        sibling_kind=SiblingKind.PATERNAL_HALF,
        label="Half-Uncle",
    )
    updated = plan.apply()
    uncle = next(person for person in updated.individuals if person.label == "Half-Uncle")
    assert KinshipEngine().sibling_kind(updated, father_id, uncle.id) == SiblingKind.PATERNAL_HALF


def test_cousin_can_be_added_before_aunt() -> None:
    proband = Individual()
    project = PedigreeProject(individuals=[proband])
    plan = KinshipEngine().plan_cousin(
        project,
        proband.id,
        branch_gender=GenderIdentity.WOMAN,
        intermediary_gender=GenderIdentity.WOMAN,
        cousin_gender=GenderIdentity.MAN,
        label="Cousin",
    )
    updated = plan.apply()
    cousin = next(person for person in updated.individuals if person.label == "Cousin")
    cousin_parents = KinshipEngine.parents(updated, cousin.id)
    assert len(cousin_parents) == 2
    assert any(
        KinshipEngine().sibling_kind(
            updated, parent_id, KinshipEngine.parents(updated, proband.id)[0]
        )
        == SiblingKind.FULL
        for parent_id in cousin_parents
    )


def test_nephew_can_be_added_before_sibling() -> None:
    proband = Individual()
    project = PedigreeProject(individuals=[proband])
    plan = KinshipEngine().plan_nephew_niece(
        project,
        proband.id,
        label="Nephew",
    )
    updated = plan.apply()
    nephew = next(person for person in updated.individuals if person.label == "Nephew")
    sibling_parent = next(
        parent_id
        for parent_id in KinshipEngine.parents(updated, nephew.id)
        if KinshipEngine().sibling_kind(updated, proband.id, parent_id) == SiblingKind.FULL
    )
    assert sibling_parent in plan.created_ids


def test_great_grandchild_creates_authorized_intermediate_path() -> None:
    root = Individual()
    project = PedigreeProject(individuals=[root])
    plan = KinshipEngine().plan_descendant(
        project,
        root.id,
        3,
        label="Great-grandchild",
        gender=GenderIdentity.WOMAN,
    )
    updated = plan.apply()
    final = next(person for person in updated.individuals if person.label == "Great-grandchild")
    assert KinshipEngine().descendants(updated, root.id)[final.id] == 3
    assert final.gender_identity == GenderIdentity.WOMAN
    assert len(plan.unknown_ids) >= 2
