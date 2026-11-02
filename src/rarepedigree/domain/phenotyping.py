"""Pure clinical phenotyping operations; no kinship inference or GUI dependency."""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Iterable
from pathlib import Path
from uuid import UUID

from rarepedigree.domain.models import (
    ClinicalObservationStatus,
    HPOObservation,
    PedigreeProject,
)


def observations_for(
    project: PedigreeProject, individual_id: UUID
) -> list[HPOObservation]:
    return [item for item in project.hpo_observations if item.individual_id == individual_id]


def latest_observation(
    project: PedigreeProject, individual_id: UUID, hpo_id: str
) -> HPOObservation | None:
    matches = [
        item
        for item in project.hpo_observations
        if item.individual_id == individual_id and item.hpo_id == hpo_id
    ]
    return max(matches, key=lambda item: item.observed_at or item.created_at, default=None)


def phenotype_matrix(
    project: PedigreeProject, individual_ids: Iterable[UUID]
) -> tuple[list[str], list[list[str]]]:
    selected = list(dict.fromkeys(individual_ids))
    terms = sorted(
        {
            item.hpo_id
            for item in project.hpo_observations
            if item.individual_id in selected
        }
    )
    rows: list[list[str]] = []
    for hpo_id in terms:
        label = next(item.term_label for item in project.hpo_observations if item.hpo_id == hpo_id)
        states = []
        for individual_id in selected:
            observation = latest_observation(project, individual_id, hpo_id)
            states.append(
                observation.status.value
                if observation
                else ClinicalObservationStatus.NOT_EVALUATED.value
            )
        rows.append([hpo_id, label, *states])
    return terms, rows


def export_phenotype_matrix_csv(
    project: PedigreeProject,
    individual_ids: Iterable[UUID],
    path: Path,
    *,
    deidentify: bool = False,
) -> None:
    selected = list(dict.fromkeys(individual_ids))
    people = {person.id: person for person in project.individuals}
    labels = []
    for individual_id in selected:
        if deidentify:
            digest = hashlib.sha256(str(individual_id).encode()).hexdigest()[:10]
            labels.append(f"RP-{digest}")
        else:
            labels.append(people[individual_id].label)
    _, rows = phenotype_matrix(project, selected)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["hpo_id", "term", *labels])
        writer.writerows(rows)
