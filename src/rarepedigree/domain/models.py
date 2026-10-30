"""Versioned domain models for the first executable pedigree prototype."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from rarepedigree.domain.states import ObservationStatus


class GenderIdentity(StrEnum):
    """Identity represented by the pedigree symbol (PED-001/PED-002)."""

    MAN = "man"
    WOMAN = "woman"
    GENDER_DIVERSE = "gender_diverse"
    UNKNOWN = "unknown"


class RelationshipKind(StrEnum):
    """Relationship kinds enabled in the Phase 4 prototype."""

    PARTNERSHIP = "partnership"
    CONSANGUINEOUS_PARTNERSHIP = "consanguineous_partnership"


class LayoutPosition(BaseModel):
    """Disposable visual position, deliberately separate from clinical facts."""

    x: float = 0.0
    y: float = 0.0


class Individual(BaseModel):
    """Minimal person representation for confirmed basic symbols."""

    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4)
    label: str = Field(default="Indivíduo", max_length=120)
    gender_identity: GenderIdentity = GenderIdentity.UNKNOWN
    phenotype_status: ObservationStatus = ObservationStatus.UNKNOWN
    deceased: bool = False
    proband: bool = False
    consultand: bool = False
    layout: LayoutPosition = Field(default_factory=LayoutPosition)


class Relationship(BaseModel):
    """A relationship edge; parentage is intentionally deferred."""

    id: UUID = Field(default_factory=uuid4)
    member_a: UUID
    member_b: UUID
    kind: RelationshipKind = RelationshipKind.PARTNERSHIP

    @model_validator(mode="after")
    def members_must_be_distinct(self) -> Relationship:
        if self.member_a == self.member_b:
            raise ValueError("a relationship requires two distinct individuals")
        return self


class PedigreeProject(BaseModel):
    """Native project document with an explicit schema version."""

    model_config = ConfigDict(validate_assignment=True)

    schema_version: str = "0.1.0"
    project_id: UUID = Field(default_factory=uuid4)
    title: str = Field(default="Heredograma sem título", max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    individuals: list[Individual] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)

    @model_validator(mode="after")
    def relationship_members_must_exist(self) -> PedigreeProject:
        individual_ids = {person.id for person in self.individuals}
        for relationship in self.relationships:
            if (
                relationship.member_a not in individual_ids
                or relationship.member_b not in individual_ids
            ):
                raise ValueError("relationship refers to an individual absent from the project")
        return self

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)
