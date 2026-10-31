from rarepedigree.domain import GenderIdentity, Individual, PedigreeProject, SiblingKind
from rarepedigree.ui.dialogs import AddRelativeWizard, ReassignBranchWizard


def _select(combo, value) -> None:
    index = combo.findData(value)
    assert index >= 0
    combo.setCurrentIndex(index)


def test_wizard_has_five_steps_and_real_scene_preview(qtbot) -> None:
    proband = Individual(label="P")
    project = PedigreeProject(individuals=[proband])
    wizard = AddRelativeWizard(project, proband)
    qtbot.addWidget(wizard)
    assert len(wizard.pageIds()) == 5
    _select(wizard.relative_kind, "maternal_grandfather")
    wizard.relative_label.setText("GF-M")
    wizard._page_changed(3)
    assert wizard.result_plan().after.individuals != project.individuals
    assert len(wizard.preview_view.scene().person_items) == 3
    assert project.individuals == [proband]


def test_wizard_cancel_never_mutates_source_project(qtbot) -> None:
    proband = Individual(label="P")
    project = PedigreeProject(individuals=[proband])
    before = project.model_dump()
    wizard = AddRelativeWizard(project, proband)
    qtbot.addWidget(wizard)
    _select(wizard.relative_kind, "maternal_cousin")
    wizard.relative_label.setText("C-M")
    wizard._page_changed(3)
    wizard.reject()
    assert project.model_dump() == before


def test_wizard_half_sibling_can_select_existing_different_parent(qtbot) -> None:
    father = Individual(label="F", gender_identity=GenderIdentity.MAN)
    mother = Individual(label="M1", gender_identity=GenderIdentity.WOMAN)
    different_mother = Individual(label="M2", gender_identity=GenderIdentity.WOMAN)
    proband = Individual(label="P")
    project = PedigreeProject(
        individuals=[father, mother, different_mother, proband],
        parentages=[
            {"parent_id": father.id, "child_id": proband.id},
            {"parent_id": mother.id, "child_id": proband.id},
        ],
    )
    wizard = AddRelativeWizard(project, proband)
    qtbot.addWidget(wizard)
    _select(wizard.relative_kind, "paternal_half_sibling")
    _select(wizard.existing_other_parent, str(different_mother.id))
    wizard.relative_label.setText("S")
    plan = wizard.build_plan()
    sibling = next(person for person in plan.after.individuals if person.label == "S")
    assert (
        wizard.engine.sibling_kind(plan.after, proband.id, sibling.id) == SiblingKind.PATERNAL_HALF
    )
    assert set(wizard.engine.parents(plan.after, sibling.id)) == {father.id, different_mother.id}


def test_branch_wizard_previews_migration_without_mutating_source(qtbot) -> None:
    from rarepedigree.domain import KinshipEngine

    engine = KinshipEngine()
    proband = Individual(label="P", proband=True)
    project = PedigreeProject(individuals=[proband])
    for gender, label in ((GenderIdentity.MAN, "F"), (GenderIdentity.WOMAN, "M")):
        project = engine.plan_ancestor_path(project, proband.id, [gender], label=label).apply()
    project = engine.plan_aunt_uncle(
        project,
        proband.id,
        branch_gender=GenderIdentity.WOMAN,
        relative_gender=GenderIdentity.WOMAN,
        label="Tia",
    ).apply()
    relative = next(person for person in project.individuals if person.label == "Tia")
    before = project.model_dump()
    wizard = ReassignBranchWizard(project, proband, relative)
    qtbot.addWidget(wizard)
    assert len(wizard.pageIds()) == 4
    plan = wizard.result_plan()
    assert project.model_dump() == before
    assert "Ramo removido" in "\n".join(plan.notes)
    assert wizard.preview.scene() is not None
