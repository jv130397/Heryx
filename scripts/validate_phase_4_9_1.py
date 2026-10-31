"""Generate the real Phase 4.9.1 visual and persistence evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    KinshipEngine,
    Parentage,
    PedigreeProject,
    SiblingKind,
)
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.rendering.exporters import export_pdf, export_png, export_svg
from rarepedigree.ui.dialogs import AddRelativeWizard
from rarepedigree.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "specifications" / "assets" / "phase_4_9_1"
OUTPUT = ROOT / "validation" / "phase_4_9_1"
ENGINE = KinshipEngine()


def person(project: PedigreeProject, label: str) -> Individual:
    return next(item for item in project.individuals if item.label == label)


def apply_layout(project: PedigreeProject) -> PedigreeProject:
    updated = project.model_copy(deep=True)
    positions = PedigreeLayoutEngine().compute(updated, preserve_locked=False)
    for item in updated.individuals:
        item.layout.x, item.layout.y = positions[item.id]
    return updated


def capture(
    app: QApplication,
    project: PedigreeProject,
    name: str,
    size: tuple[int, int] = (1366, 768),
) -> Path:
    window = MainWindow()
    window.resize(*size)
    window._apply_project(apply_layout(project))
    window.show()
    app.processEvents()
    window.fit_pedigree()
    app.processEvents()
    path = ASSETS / f"{name}.png"
    window.grab().save(str(path))
    window.undo_stack.setClean()
    window.close()
    return path


def base_proband(
    gender: GenderIdentity = GenderIdentity.UNKNOWN,
) -> tuple[PedigreeProject, Individual]:
    proband = Individual(label="P", gender_identity=gender, proband=True)
    return PedigreeProject(title="Validação 4.9.1", individuals=[proband]), proband


def ancestor_family(depth: int) -> PedigreeProject:
    project, proband = base_proband()
    frontier = [proband.id]
    for _ in range(depth - 1):
        next_frontier = []
        for child_id in frontier:
            project, parent_ids = FamilyService.add_parents(project, child_id)
            next_frontier.extend(parent_ids)
        frontier = next_frontier
    return project


def half_siblings(kind: SiblingKind) -> PedigreeProject:
    project, proband = base_proband()
    project, _ = FamilyService.add_parents(project, proband.id)
    plan = ENGINE.plan_sibling(project, proband.id, kind, label="S")
    return plan.apply()


def three_coparents(parent_gender: GenderIdentity) -> PedigreeProject:
    project, root = base_proband(parent_gender)
    other_gender = (
        GenderIdentity.WOMAN if parent_gender == GenderIdentity.MAN else GenderIdentity.MAN
    )
    for index in range(3):
        coparent = Individual(label=f"C{index + 1}", gender_identity=other_gender)
        project.individuals.append(coparent)
        project = ENGINE.plan_child(
            project,
            root.id,
            coparent_id=coparent.id,
            label=f"F{index + 1}",
        ).apply()
    return project


def collateral_family() -> PedigreeProject:
    project, proband = base_proband()
    project = ENGINE.plan_cousin(
        project,
        proband.id,
        branch_gender=GenderIdentity.WOMAN,
        intermediary_gender=GenderIdentity.WOMAN,
        cousin_gender=GenderIdentity.MAN,
        label="Primo-M",
    ).apply()
    project = ENGINE.plan_aunt_uncle(
        project,
        proband.id,
        branch_gender=GenderIdentity.MAN,
        relative_gender=GenderIdentity.MAN,
        label="Tio-P",
    ).apply()
    return project


def unknown_family() -> PedigreeProject:
    project, proband = base_proband(GenderIdentity.MAN)
    return ENGINE.plan_child(project, proband.id, label="Filho").apply()


def large_family(size: int = 50) -> PedigreeProject:
    project = PedigreeProject(title="Família extensa")
    counter = 0

    def new_person(gender: GenderIdentity) -> Individual:
        nonlocal counter
        counter += 1
        item = Individual(label=f"E{counter}", gender_identity=gender)
        project.individuals.append(item)
        return item

    founder_a = new_person(GenderIdentity.MAN)
    founder_b = new_person(GenderIdentity.WOMAN)
    generation = []
    for index in range(4):
        child = new_person(GenderIdentity.MAN if index % 2 == 0 else GenderIdentity.WOMAN)
        generation.append(child)
        project.parentages.extend(
            Parentage(parent_id=parent.id, child_id=child.id)
            for parent in (founder_a, founder_b)
        )
    next_generation = []
    for index, parent in enumerate(generation):
        partner = new_person(
            GenderIdentity.WOMAN
            if parent.gender_identity == GenderIdentity.MAN
            else GenderIdentity.MAN
        )
        for child_index in range(3):
            child = new_person(
                GenderIdentity.MAN if (index + child_index) % 2 == 0 else GenderIdentity.WOMAN
            )
            next_generation.append(child)
            project.parentages.extend(
                Parentage(parent_id=item.id, child_id=child.id) for item in (parent, partner)
            )
    for index, parent in enumerate(next_generation[:8]):
        partner = new_person(
            GenderIdentity.WOMAN
            if parent.gender_identity == GenderIdentity.MAN
            else GenderIdentity.MAN
        )
        for child_index in range(2):
            child = new_person(
                GenderIdentity.MAN if (index + child_index) % 2 == 0 else GenderIdentity.WOMAN
            )
            project.parentages.extend(
                Parentage(parent_id=item.id, child_id=child.id) for item in (parent, partner)
            )
    while len(project.individuals) < size:
        project = ENGINE.plan_sibling(
            project, next_generation[len(project.individuals) % len(next_generation)].id,
            SiblingKind.FULL, label=f"E{len(project.individuals) + 1}"
        ).apply()
    return project


def final_demo() -> PedigreeProject:
    project, proband = base_proband(GenderIdentity.MAN)
    # Mixed order: collateral and siblings are deliberately inserted before
    # all named ancestors have been completed.
    project = ENGINE.plan_cousin(
        project,
        proband.id,
        branch_gender=GenderIdentity.WOMAN,
        intermediary_gender=GenderIdentity.WOMAN,
        label="Primo-M",
    ).apply()
    project = ENGINE.plan_sibling(project, proband.id, SiblingKind.FULL, label="Irmão-1").apply()
    project = ENGINE.plan_sibling(project, proband.id, SiblingKind.FULL, label="Irmão-2").apply()
    project = ENGINE.plan_sibling(
        project, proband.id, SiblingKind.PATERNAL_HALF, label="Meio-irmão-P"
    ).apply()
    project = ENGINE.plan_sibling(
        project, proband.id, SiblingKind.MATERNAL_HALF, label="Meia-irmã-M"
    ).apply()
    person(project, "Meia-irmã-M").gender_identity = GenderIdentity.WOMAN
    project = ENGINE.plan_aunt_uncle(
        project,
        proband.id,
        branch_gender=GenderIdentity.MAN,
        relative_gender=GenderIdentity.MAN,
        label="Tio-P",
    ).apply()
    project = ENGINE.plan_child(project, person(project, "Tio-P").id, label="Primo-P").apply()
    project = ENGINE.plan_nephew_niece(
        project,
        proband.id,
        sibling_id=person(project, "Irmão-1").id,
        label="Sobrinho",
    ).apply()
    # Identify one structural unknown through reconciliation.
    unknown = next(item for item in project.individuals if item.placeholder)
    identified = Individual(label="Familiar identificado", gender_identity=unknown.gender_identity)
    project.individuals.append(identified)
    project = ENGINE.reconcile_unknown(project, unknown.id, identified.id).apply()
    return PedigreeProject.model_validate(project.model_dump())


def capture_wizard(app: QApplication, preview: bool) -> Path:
    project, proband = base_proband()
    wizard = AddRelativeWizard(project, proband)
    wizard.resize(960, 680)
    wizard.relative_label.setText("Primo materno")
    wizard.relative_kind.setCurrentIndex(wizard.relative_kind.findData("maternal_cousin"))
    if preview:
        wizard.setStartId(3)
        wizard._page_changed(3)
    wizard.show()
    app.processEvents()
    name = "10_wizard_preview" if preview else "09_relative_wizard"
    path = ASSETS / f"{name}.png"
    wizard.grab().save(str(path))
    wizard.close()
    return path


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    evidence = {
        "01_three_generations": capture(app, ancestor_family(3), "01_three_generations"),
        "02_four_generations": capture(app, ancestor_family(4), "02_four_generations"),
        "03_paternal_half_siblings": capture(
            app, half_siblings(SiblingKind.PATERNAL_HALF), "03_paternal_half_siblings"
        ),
        "04_maternal_half_siblings": capture(
            app, half_siblings(SiblingKind.MATERNAL_HALF), "04_maternal_half_siblings"
        ),
        "05_father_three_mothers": capture(
            app, three_coparents(GenderIdentity.MAN), "05_father_three_mothers"
        ),
        "06_mother_three_fathers": capture(
            app, three_coparents(GenderIdentity.WOMAN), "06_mother_three_fathers"
        ),
        "07_aunts_cousins": capture(app, collateral_family(), "07_aunts_cousins"),
        "08_unknown_people": capture(app, unknown_family(), "08_unknown_people"),
        "09_relative_wizard": capture_wizard(app, False),
        "10_wizard_preview": capture_wizard(app, True),
        "11_large_family_50": capture(app, large_family(), "11_large_family_50", size=(2560, 1440)),
    }
    demo = apply_layout(final_demo())
    repository = JsonProjectRepository()
    project_path = OUTPUT / "phase_4_9_1_demo.rps.json"
    repository.save(demo, project_path)
    reopened = repository.load(project_path)
    window = MainWindow()
    window._apply_project(reopened)
    export_svg(window.scene, OUTPUT / "phase_4_9_1_demo.svg")
    export_png(window.scene, OUTPUT / "phase_4_9_1_demo.png")
    export_pdf(window.scene, OUTPUT / "phase_4_9_1_demo.pdf")
    window.undo_stack.setClean()
    window.close()
    result = {
        "individuals": len(reopened.individuals),
        "parentages": len(reopened.parentages),
        "relationships": len(reopened.relationships),
        "captures": {key: str(value.relative_to(ROOT)) for key, value in evidence.items()},
        "project": str(project_path.relative_to(ROOT)),
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
