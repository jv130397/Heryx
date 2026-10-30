from uuid import uuid4

import pytest
from pydantic import ValidationError

from rarepedigree.domain import Individual, PedigreeProject, Relationship


def test_relationship_members_must_exist() -> None:
    person = Individual(label="I-1")
    with pytest.raises(ValidationError, match="absent from the project"):
        PedigreeProject(
            individuals=[person],
            relationships=[Relationship(member_a=person.id, member_b=uuid4())],
        )


def test_native_model_round_trip_preserves_unknown_state() -> None:
    project = PedigreeProject(individuals=[Individual(label="I-1")])
    restored = PedigreeProject.model_validate_json(project.model_dump_json())
    assert restored == project
    assert restored.individuals[0].phenotype_status.value == "unknown"

