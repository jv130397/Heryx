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
    SEPARATED_PARTNERSHIP = "separated_partnership"
    DIVORCED_PARTNERSHIP = "divorced_partnership"


class ParentageKind(StrEnum):
    BIOLOGICAL = "biological"
    GESTATIONAL = "gestational"
    LEGAL = "legal"
    SOCIAL = "social"
    UNKNOWN = "unknown"


class EvidenceStatus(StrEnum):
    """How a fact entered the pedigree; orthogonal to its scientific kind."""

    CONFIRMED = "confirmed"
    DERIVED = "derived"
    PROVISIONAL = "provisional"
    UNKNOWN = "unknown"


class DeclaredKinshipKind(StrEnum):
    """Relations that cannot always be reduced to known parentage yet."""

    SIBLING_UNRESOLVED = "sibling_unresolved"
    ADOPTIVE_SIBLING = "adoptive_sibling"
    SOCIAL_SIBLING = "social_sibling"


class TwinZygosity(StrEnum):
    MONOZYGOTIC = "monozygotic"
    DIZYGOTIC = "dizygotic"
    UNKNOWN = "unknown"


class AnnotationType(StrEnum):
    GENERAL = "general"
    REVIEW = "review"
    TO_CONFIRM = "to_confirm"
    TECHNICAL = "technical"


class LayoutPosition(BaseModel):
    """Disposable visual position, deliberately separate from clinical facts."""

    x: float = 0.0
    y: float = 0.0
    locked: bool = False


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
    placeholder: bool = False
    unknown_reason: str | None = Field(default=None, max_length=200)
    provenance: str | None = Field(default=None, max_length=200)
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


class Parentage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    parent_id: UUID
    child_id: UUID
    kind: ParentageKind = ParentageKind.BIOLOGICAL
    evidence_status: EvidenceStatus = EvidenceStatus.CONFIRMED
    provenance: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def parent_and_child_must_differ(self) -> Parentage:
        if self.parent_id == self.child_id:
            raise ValueError("an individual cannot be their own parent")
        return self


class TwinGroup(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    member_ids: list[UUID] = Field(min_length=2)
    zygosity: TwinZygosity = TwinZygosity.UNKNOWN


class DeclaredKinship(BaseModel):
    """Explicit kinship assertion retained until its graph path is known."""

    id: UUID = Field(default_factory=uuid4)
    member_a: UUID
    member_b: UUID
    kind: DeclaredKinshipKind
    evidence_status: EvidenceStatus = EvidenceStatus.CONFIRMED
    provenance: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def members_must_be_distinct(self) -> DeclaredKinship:
        if self.member_a == self.member_b:
            raise ValueError("a kinship assertion requires two distinct individuals")
        return self


class Family(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str = Field(default="Família", max_length=200)


class CanvasAnnotation(BaseModel):
    """User-authored canvas comment, deliberately outside clinical facts."""

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(default="Anotação", max_length=120)
    text: str = Field(default="", max_length=4000)
    x: float = 0.0
    y: float = 0.0
    width: float = Field(default=220.0, ge=140.0, le=600.0)
    height: float = Field(default=150.0, ge=100.0, le=500.0)
    kind: AnnotationType = AnnotationType.GENERAL
    color: str = Field(default="#FFF2B3", max_length=20)
    individual_id: UUID | None = None
    visible: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PedigreeProject(BaseModel):
    """Native project document with an explicit schema version."""

    model_config = ConfigDict(validate_assignment=True)

    schema_version: str = "0.3.0"
    project_id: UUID = Field(default_factory=uuid4)
    title: str = Field(default="Heredograma sem título", max_length=200)
    description: str = Field(default="", max_length=1000)
    project_language: str = Field(default="pt_BR", max_length=10)
    representation: str = Field(default="scientific", max_length=30)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    individuals: list[Individual] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    parentages: list[Parentage] = Field(default_factory=list)
    twin_groups: list[TwinGroup] = Field(default_factory=list)
    declared_kinships: list[DeclaredKinship] = Field(default_factory=list)
    annotations: list[CanvasAnnotation] = Field(default_factory=list)
    family: Family = Field(default_factory=Family)

    @model_validator(mode="after")
    def relationship_members_must_exist(self) -> PedigreeProject:
        individual_ids = {person.id for person in self.individuals}
        for annotation in self.annotations:
            if (
                annotation.individual_id is not None
                and annotation.individual_id not in individual_ids
            ):
                annotation.individual_id = None
        for relationship in self.relationships:
            if (
                relationship.member_a not in individual_ids
                or relationship.member_b not in individual_ids
            ):
                raise ValueError("relationship refers to an individual absent from the project")
        for parentage in self.parentages:
            if (
                parentage.parent_id not in individual_ids
                or parentage.child_id not in individual_ids
            ):
                raise ValueError("parentage refers to an individual absent from the project")
        self._validate_parentage_cycles()
        for group in self.twin_groups:
            if len(set(group.member_ids)) != len(group.member_ids):
                raise ValueError("twin group contains duplicate members")
            if any(member_id not in individual_ids for member_id in group.member_ids):
                raise ValueError("twin group refers to an individual absent from the project")
        for assertion in self.declared_kinships:
            if assertion.member_a not in individual_ids or assertion.member_b not in individual_ids:
                raise ValueError("declared kinship refers to an individual absent from the project")
        return self

    def _validate_parentage_cycles(self) -> None:
        children: dict[UUID, set[UUID]] = {}
        for edge in self.parentages:
            children.setdefault(edge.parent_id, set()).add(edge.child_id)
        visiting: set[UUID] = set()
        visited: set[UUID] = set()

        def visit(node: UUID) -> None:
            if node in visiting:
                raise ValueError("parentage graph contains a cycle")
            if node in visited:
                return
            visiting.add(node)
            for child in children.get(node, set()):
                visit(child)
            visiting.remove(node)
            visited.add(node)

        for node in children:
            visit(node)

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)
