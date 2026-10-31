"""Generate authentic before/after evidence and metrics for Phase 4.9.2."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import (
    ancestor_family,
    collateral_family,
    large_family,
    three_coparents,
)

from rarepedigree.domain import GenderIdentity, Individual, KinshipEngine, PedigreeProject
from rarepedigree.layout import PedigreeLayoutEngine, audit_parentage_connectors, measure_scene
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.rendering import PedigreeScene
from rarepedigree.rendering.exporters import export_pdf, export_png, export_svg
from rarepedigree.ui.dialogs import ReassignBranchWizard
from rarepedigree.ui.main_window import MainWindow

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "specifications" / "assets" / "phase_4_9_2"
OUTPUT = ROOT / "validation" / "phase_4_9_2"
ENGINE = KinshipEngine()


def layout(project: PedigreeProject) -> PedigreeProject:
    result = project.model_copy(deep=True)
    positions = PedigreeLayoutEngine().compute(result, preserve_locked=False)
    for person in result.individuals:
        person.layout.x, person.layout.y = positions[person.id]
    return result


def metrics(project: PedigreeProject) -> dict[str, int | float]:
    scene = PedigreeScene()
    scene.load_project(layout(project))
    return measure_scene(scene).__dict__


def connector_audit(project: PedigreeProject) -> list[dict[str, object]]:
    scene = PedigreeScene()
    scene.load_project(layout(project))
    return audit_parentage_connectors(scene)


def capture(app: QApplication, project: PedigreeProject, name: str) -> Path:
    window = MainWindow()
    window.resize(1920, 1080)
    window._apply_project(layout(project))
    window.show()
    app.processEvents()
    window.fit_pedigree()
    app.processEvents()
    path = ASSETS / f"{name}.png"
    window.grab().save(str(path))
    window.close()
    return path


def branch_scenario() -> tuple[PedigreeProject, Individual, Individual]:
    proband = Individual(label="P", proband=True)
    project = PedigreeProject(title="Migração de ramo", individuals=[proband])
    for gender, label in ((GenderIdentity.MAN, "Pai"), (GenderIdentity.WOMAN, "Mãe")):
        project = ENGINE.plan_ancestor_path(project, proband.id, [gender], label=label).apply()
    project = ENGINE.plan_cousin(
        project,
        proband.id,
        branch_gender=GenderIdentity.WOMAN,
        intermediary_gender=GenderIdentity.WOMAN,
        cousin_gender=GenderIdentity.MAN,
        label="Primo",
    ).apply()
    cousin = next(person for person in project.individuals if person.label == "Primo")
    return project, proband, cousin


def capture_branch_wizard(
    app: QApplication, project: PedigreeProject, proband: Individual, cousin: Individual
) -> Path:
    wizard = ReassignBranchWizard(project, proband, cousin)
    wizard.resize(960, 720)
    wizard.setStartId(2)
    wizard._refresh()
    wizard.show()
    app.processEvents()
    path = ASSETS / "branch_migration_preview.png"
    wizard.grab().save(str(path))
    wizard.close()
    return path


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    scenarios = {
        "four_generations": ancestor_family(4),
        "father_three_mothers": three_coparents(GenderIdentity.MAN),
        "mother_three_fathers": three_coparents(GenderIdentity.WOMAN),
        "aunts_cousins": collateral_family(),
        "extended_50": large_family(),
    }
    evidence = {
        name: str(capture(app, project, f"after_{name}").relative_to(ROOT))
        for name, project in scenarios.items()
    }
    branch_before, proband, cousin = branch_scenario()
    branch_plan = ENGINE.plan_reassign_collateral_branch(
        branch_before, proband.id, cousin.id, GenderIdentity.MAN
    )
    branch_after = branch_plan.apply()
    evidence["branch_before"] = str(
        capture(app, branch_before, "branch_before").relative_to(ROOT)
    )
    evidence["branch_after"] = str(
        capture(app, branch_after, "branch_after").relative_to(ROOT)
    )
    evidence["branch_wizard"] = str(
        capture_branch_wizard(app, branch_before, proband, cousin).relative_to(ROOT)
    )

    persisted = layout(branch_after)
    repository = JsonProjectRepository()
    project_path = OUTPUT / "branch_migration_demo.rps.json"
    repository.save(persisted, project_path)
    reopened = repository.load(project_path)
    scene = PedigreeScene()
    scene.load_project(reopened)
    export_svg(scene, OUTPUT / "branch_migration_demo.svg")
    export_png(scene, OUTPUT / "branch_migration_demo.png")
    export_pdf(scene, OUTPUT / "branch_migration_demo.pdf")
    result = {
        "baseline_captures": "specifications/assets/phase_4_9_1",
        "evidence": evidence,
        "metrics": {name: metrics(project) for name, project in scenarios.items()},
        "connector_audit": {
            name: connector_audit(project) for name, project in scenarios.items()
        },
        "branch_before": metrics(branch_before),
        "branch_after": metrics(branch_after),
        "branch_notes": branch_plan.notes,
        "persisted_project": str(project_path.relative_to(ROOT)),
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
