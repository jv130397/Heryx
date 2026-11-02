"""Reproducible, synthetic-only Phase 4.13 performance measurements."""

from __future__ import annotations

import json
import tempfile
import time
import tracemalloc
from pathlib import Path

from rarepedigree.domain import (
    ClinicalObservationStatus,
    HPOObservation,
    Individual,
    PedigreeProject,
    phenotype_matrix,
)
from rarepedigree.persistence import JsonProjectRepository
from rarepedigree.terminology import HPOIndex

ROOT = Path(__file__).resolve().parents[1]


def elapsed_ms(operation, repetitions: int = 1) -> float:
    started = time.perf_counter()
    for _ in range(repetitions):
        operation()
    return (time.perf_counter() - started) * 1000 / repetitions


def main() -> None:
    people = [Individual(label=f"SYN-{index:03d}") for index in range(200)]
    observations = [
        HPOObservation(
            individual_id=person.id,
            hpo_id="HP:0001250",
            term_label="Seizure",
            status=(
                ClinicalObservationStatus.PRESENT
                if index % 2
                else ClinicalObservationStatus.ABSENT
            ),
            ontology_version="benchmark-synthetic",
        )
        for index, person in enumerate(people)
    ]
    project = PedigreeProject(individuals=people, hpo_observations=observations)
    index = HPOIndex()
    tracemalloc.start()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "benchmark.rps.json"
        save_ms = elapsed_ms(lambda: JsonProjectRepository().save(project, path), 5)
        load_ms = elapsed_ms(lambda: JsonProjectRepository().load(path), 5)
    matrix_ms = elapsed_ms(lambda: phenotype_matrix(project, [p.id for p in people]), 50)
    search_ms = (
        elapsed_ms(lambda: index.search("seizure", 20), 100) if index.installed else None
    )
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result = {
        "synthetic_people": 200,
        "synthetic_observations": 200,
        "hpo_installed_terms": index.metadata().term_count if index.installed else 0,
        "mean_hpo_search_ms": search_ms,
        "mean_matrix_ms": matrix_ms,
        "mean_save_ms": save_ms,
        "mean_load_ms": load_ms,
        "peak_python_memory_mib": peak / 1024 / 1024,
    }
    output = ROOT / "validation" / "phase_4_13"
    output.mkdir(parents=True, exist_ok=True)
    (output / "performance.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
