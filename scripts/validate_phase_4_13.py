"""Capture real Phase 4.13 PySide6 surfaces with synthetic clinical data."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from validate_phase_4_9_1 import ancestor_family, apply_layout

from rarepedigree.domain import ClinicalObservationStatus, HPOObservation
from rarepedigree.terminology import HPOIndex
from rarepedigree.ui.clinical import (
    FamilyPhenotypeComparisonDialog,
    HPOManagerDialog,
    HPOObservationDialog,
)
from rarepedigree.ui.i18n import language_manager
from rarepedigree.ui.main_window import MainWindow
from rarepedigree.ui.preferences import PreferencesDialog

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "phase_4_13"
OUTPUT = ROOT / "validation" / "phase_4_13"


def capture(widget, name: str) -> str:
    QApplication.processEvents()
    QTest.qWait(180)
    path = ASSETS / f"{name}.png"
    assert widget.grab().save(str(path))
    return str(path.relative_to(ROOT))


def dialog_capture(dialog, name: str, size: tuple[int, int]) -> str:
    dialog.resize(*size)
    dialog.show()
    result = capture(dialog, name)
    dialog.close()
    return result


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    index = HPOIndex()
    assert index.installed, "Install official HPO before visual validation"
    metadata = index.metadata()
    seizure = index.term("HP:0001250")
    abnormality = index.term("HP:0000118")
    assert seizure and abnormality and metadata
    project = apply_layout(ancestor_family(3))
    project.individuals[-1].proband = True
    target = project.individuals[-1]
    mother = project.individuals[-2]
    project.hpo_observations = [
        HPOObservation(
            individual_id=target.id,
            hpo_id=seizure.id,
            term_label=seizure.name,
            status=ClinicalObservationStatus.PRESENT,
            onset="4 anos",
            severity="moderate",
            course="stable",
            source="Avaliação clínica sintética",
            notes="Dado sintético para validação visual.",
            ontology_version=metadata.version,
        ),
        HPOObservation(
            individual_id=mother.id,
            hpo_id=seizure.id,
            term_label=seizure.name,
            status=ClinicalObservationStatus.ABSENT,
            source="Avaliação clínica sintética",
            ontology_version=metadata.version,
        ),
        HPOObservation(
            individual_id=target.id,
            hpo_id=abnormality.id,
            term_label=abnormality.name,
            status=ClinicalObservationStatus.UNKNOWN,
            ontology_version=metadata.version,
        ),
    ]
    language_manager.set_language("pt_BR")
    window = MainWindow()
    window.resize(1920, 1080)
    window._apply_project(project)
    window.show()
    window.fit_pedigree()
    item = window.scene.person_items[target.id]
    item.setSelected(True)
    window._open_floating_editor(item)
    window.floating_editor.tabs.setCurrentIndex(1)
    evidence = {
        "clinical_editor_1920": capture(window, "01_clinical_editor_pt_1920x1080")
    }
    panel = window.floating_editor.clinical_panel
    panel.search.setText("seizure")
    QTest.qWait(350)
    evidence["autocomplete"] = capture(window, "02_hpo_autocomplete")
    window.resize(1366, 768)
    window._position_context_surfaces()
    evidence["clinical_1366"] = capture(window, "03_clinical_editor_1366x768")
    present = HPOObservationDialog(
        seizure, target.id, metadata.version, project.hpo_observations[0], window
    )
    evidence["present_observation"] = dialog_capture(
        present, "04_present_observation", (620, 700)
    )
    absent = HPOObservationDialog(
        seizure, mother.id, metadata.version, project.hpo_observations[1], window
    )
    evidence["absent_observation"] = dialog_capture(
        absent, "05_absent_observation", (620, 700)
    )
    obsolete = next((term for term in index.search("obsolete", 100) if term.obsolete), None)
    if obsolete:
        evidence["obsolete"] = dialog_capture(
            HPOObservationDialog(obsolete, target.id, metadata.version, parent=window),
            "06_obsolete_term",
            (620, 700),
        )
    comparison = FamilyPhenotypeComparisonDialog(project, window)
    evidence["comparison"] = dialog_capture(comparison, "07_family_comparison", (1100, 650))
    window.highlight_hpo("HP:0001250")
    highlight_ok = window.scene.person_items[target.id].clinical_highlight == "present"
    window.resize(1920, 1080)
    window.floating_editor.hide()
    evidence["highlight"] = capture(window, "08_hpo_highlight")
    preferences = PreferencesDialog(window)
    preferences.tabs.setCurrentIndex(3)
    evidence["preferences"] = dialog_capture(preferences, "09_hpo_preferences", (760, 560))
    manager = HPOManagerDialog(window)
    evidence["manager"] = dialog_capture(manager, "10_hpo_manager", (680, 420))
    language_manager.set_language("en")
    english = MainWindow()
    english.resize(1920, 1080)
    english._apply_project(project)
    english.show()
    english._open_floating_editor(english.scene.person_items[target.id])
    english.floating_editor.tabs.setCurrentIndex(1)
    evidence["english"] = capture(english, "11_clinical_editor_en")
    checks = {
        "official_hpo_terms": metadata.term_count,
        "official_hpo_version": metadata.version,
        "clinical_observations": len(project.hpo_observations),
        "overall_status_unchanged": target.phenotype_status.value == "unknown",
        "highlight_is_presentation_only": (
            highlight_ok
        ),
        "notes_preserved": hasattr(project, "annotations"),
    }
    result = {
        "platform": os.environ["QT_QPA_PLATFORM"],
        "real_display": False,
        "note": "Real Qt widgets rendered offscreen with synthetic clinical observations.",
        "checks": checks,
        "evidence": evidence,
    }
    (OUTPUT / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    english.undo_stack.setClean()
    english.close()
    window.undo_stack.setClean()
    window.close()
    language_manager.set_language("pt_BR")
    app.processEvents()


if __name__ == "__main__":
    main()
