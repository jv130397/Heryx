from pathlib import Path

import pytest
from pydantic import ValidationError

from rarepedigree.domain import (
    CanvasAnnotation,
    ClinicalObservationStatus,
    ClinicalSeverity,
    GenderIdentity,
    HPOObservation,
    Individual,
    PedigreeProject,
    export_phenotype_matrix_csv,
    phenotype_matrix,
)
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.persistence.migrations import migrate_project
from rarepedigree.rendering import PedigreeScene
from rarepedigree.terminology import HPOIndex, build_hpo_database, parse_obo
from rarepedigree.ui.i18n import language_manager, tr
from rarepedigree.ui.main_window import MainWindow

OBO = """format-version: 1.2
data-version: hp/releases/2026-09-01
date: 01:09:2026 12:00

[Term]
id: HP:0000118
name: Phenotypic abnormality
def: "A phenotypic abnormality."

[Term]
id: HP:0001250
name: Seizure
def: "A transient occurrence of signs due to abnormal neuronal activity."
synonym: "Epileptic seizure" EXACT []
is_a: HP:0000118 ! Phenotypic abnormality

[Term]
id: HP:0000001
name: obsolete Old seizure
is_obsolete: true
replaced_by: HP:0001250
alt_id: HP:9999999
"""


@pytest.fixture
def hpo_index(tmp_path: Path) -> HPOIndex:
    source = tmp_path / "hp.obo"
    source.write_text(OBO, encoding="utf-8")
    database = tmp_path / "hpo.sqlite3"
    build_hpo_database(source, database, source="synthetic-test", minimum_terms=3)
    source.unlink()
    return HPOIndex(database)


def test_official_obo_fields_are_parsed(tmp_path: Path) -> None:
    source = tmp_path / "hp.obo"
    source.write_text(OBO, encoding="utf-8")
    header, terms = parse_obo(source)
    assert header["data-version"] == "hp/releases/2026-09-01"
    assert terms[1].synonyms == ["Epileptic seizure"]
    assert terms[1].parents == ["HP:0000118"]


def test_hpo_search_by_identifier_name_and_synonym(hpo_index: HPOIndex) -> None:
    assert hpo_index.search("HP:0001250")[0].name == "Seizure"
    assert hpo_index.search("Seiz")[0].id == "HP:0001250"
    assert hpo_index.search("Epileptic")[0].id == "HP:0001250"


def test_hpo_obsolete_replacement_and_alternative_id(hpo_index: HPOIndex) -> None:
    obsolete = hpo_index.term("HP:9999999")
    assert obsolete is not None
    assert obsolete.obsolete
    assert obsolete.replaced_by == "HP:0001250"


def test_hpo_index_works_offline_after_source_is_removed(
    hpo_index: HPOIndex, tmp_path: Path
) -> None:
    assert not (tmp_path / "hp.obo").exists()
    assert hpo_index.search("Seizure")[0].id == "HP:0001250"
    assert hpo_index.metadata().term_count == 3


def test_failed_index_build_preserves_previous_database(
    hpo_index: HPOIndex, tmp_path: Path
) -> None:
    original = hpo_index.path.read_bytes()
    invalid = tmp_path / "invalid.obo"
    invalid.write_text("format-version: 1.2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity check"):
        build_hpo_database(invalid, hpo_index.path, minimum_terms=1)
    assert hpo_index.path.read_bytes() == original
    assert hpo_index.search("Seizure")[0].id == "HP:0001250"


def test_all_clinical_observation_states_are_distinct() -> None:
    assert {item.value for item in ClinicalObservationStatus} == {
        "present",
        "absent",
        "unknown",
        "not_evaluated",
    }


def test_schema_0_3_migration_preserves_notes_and_does_not_invent_clinical_data() -> None:
    project = PedigreeProject(annotations=[CanvasAnnotation(title="Keep")])
    raw = project.model_dump(mode="json")
    raw["schema_version"] = "0.3.0"
    raw.pop("hpo_observations")
    migrated = migrate_project(raw)
    assert migrated["schema_version"] == "0.4.0"
    assert migrated["annotations"][0]["title"] == "Keep"
    assert migrated["hpo_observations"] == []


def test_phase_4_13_clinical_strings_translate_to_english() -> None:
    language_manager.set_language("en")
    try:
        assert tr("Comparação fenotípica familiar") == "Family phenotype comparison"
        assert tr("Não avaliado") == "Not evaluated"
    finally:
        language_manager.set_language("pt_BR")


def test_hpo_observation_does_not_change_overall_phenotype() -> None:
    person = Individual()
    observation = HPOObservation(
        individual_id=person.id,
        hpo_id="HP:0001250",
        term_label="Seizure",
        status=ClinicalObservationStatus.PRESENT,
        severity=ClinicalSeverity.MODERATE,
        onset="4 years",
        ontology_version="2026-09-01",
    )
    project = PedigreeProject(individuals=[person], hpo_observations=[observation])
    assert project.individuals[0].phenotype_status.value == "unknown"


def test_duplicate_same_term_person_and_date_is_rejected() -> None:
    person = Individual()
    observation = HPOObservation(
        individual_id=person.id,
        hpo_id="HP:0001250",
        term_label="Seizure",
        ontology_version="2026-09-01",
    )
    with pytest.raises(ValidationError, match="duplicate HPO"):
        PedigreeProject(
            individuals=[person],
            hpo_observations=[observation, observation.model_copy(update={"id": None})],
        )


def test_clinical_data_notes_and_family_round_trip(tmp_path: Path) -> None:
    person = Individual(label="I-1")
    project = PedigreeProject(
        individuals=[person],
        annotations=[CanvasAnnotation(title="Visual")],
        hpo_observations=[
            HPOObservation(
                individual_id=person.id,
                hpo_id="HP:0001250",
                term_label="Seizure",
                status=ClinicalObservationStatus.ABSENT,
                source="Synthetic evaluation",
                ontology_version="2026-09-01",
            )
        ],
    )
    path = tmp_path / "clinical.rps.json"
    JsonProjectRepository().save(project, path)
    loaded = JsonProjectRepository().load(path)
    assert loaded.hpo_observations[0].status == ClinicalObservationStatus.ABSENT
    assert loaded.annotations[0].title == "Visual"
    assert loaded.individuals[0].id == person.id


def test_family_matrix_never_infers_unrecorded_absence(tmp_path: Path) -> None:
    proband, sibling = Individual(label="P"), Individual(label="S")
    project = PedigreeProject(
        individuals=[proband, sibling],
        hpo_observations=[
            HPOObservation(
                individual_id=proband.id,
                hpo_id="HP:0001250",
                term_label="Seizure",
                status=ClinicalObservationStatus.PRESENT,
                ontology_version="2026-09-01",
            )
        ],
    )
    _, rows = phenotype_matrix(project, [proband.id, sibling.id])
    assert rows[0][2:] == ["present", "not_evaluated"]
    path = tmp_path / "matrix.csv"
    export_phenotype_matrix_csv(project, [proband.id, sibling.id], path, deidentify=True)
    content = path.read_text(encoding="utf-8")
    assert "not_evaluated" in content
    header = content.splitlines()[0]
    assert ",P," not in header and not header.endswith(",S")


def test_hpo_highlight_is_temporary_presentation_only(qapp) -> None:
    del qapp
    person = Individual()
    project = PedigreeProject(individuals=[person])
    scene = PedigreeScene()
    scene.load_project(project)
    scene.set_clinical_highlights({person.id: "present"})
    assert scene.person_items[person.id].clinical_highlight == "present"
    assert project.individuals[0].phenotype_status.value == "unknown"
    scene.set_clinical_highlights()
    assert scene.person_items[person.id].clinical_highlight is None


def test_editor_clinical_save_is_atomic_and_undoable(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.UNKNOWN)
    item = window.scene.person_items[person.id]
    window._open_floating_editor(item)
    window.floating_editor.clinical_panel.observations = [
        HPOObservation(
            individual_id=person.id,
            hpo_id="HP:0001250",
            term_label="Seizure",
            status=ClinicalObservationStatus.PRESENT,
            ontology_version="2026-09-01",
        )
    ]
    window.floating_editor.label_edit.setText("P")
    window.floating_editor._save()
    assert window.project.hpo_observations[0].hpo_id == "HP:0001250"
    assert window.project.individuals[0].label == "P"
    window.undo_stack.undo()
    assert not window.project.hpo_observations


def test_cancelled_editor_does_not_persist_local_clinical_changes(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    person = window.add_person(GenderIdentity.UNKNOWN)
    window._open_floating_editor(window.scene.person_items[person.id])
    window.floating_editor.clinical_panel.observations.append(
        HPOObservation(
            individual_id=person.id,
            hpo_id="HP:0001250",
            term_label="Seizure",
            ontology_version="2026-09-01",
        )
    )
    window.floating_editor.request_close()
    assert not window.project.hpo_observations
