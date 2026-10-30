"""Qt-independent kinship inference, planning and atomic graph mutations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from pydantic import ValidationError

from rarepedigree.domain.models import (
    DeclaredKinship,
    DeclaredKinshipKind,
    EvidenceStatus,
    GenderIdentity,
    Individual,
    Parentage,
    ParentageKind,
    PedigreeProject,
)


class SiblingKind(StrEnum):
    FULL = "full"
    PATERNAL_HALF = "paternal_half"
    MATERNAL_HALF = "maternal_half"
    UNRESOLVED = "unresolved"
    ADOPTIVE = "adoptive"
    SOCIAL = "social"


class KinshipSeverity(StrEnum):
    ERROR = "error"
    AMBIGUITY = "ambiguity"
    WARNING = "warning"


@dataclass(frozen=True)
class KinshipIssue:
    severity: KinshipSeverity
    code: str
    message: str
    person_ids: tuple[UUID, ...] = ()


@dataclass
class KinshipPlan:
    """Previewable operation; applying it is an all-or-nothing replacement."""

    label: str
    before: PedigreeProject
    after: PedigreeProject
    created_ids: list[UUID] = field(default_factory=list)
    reused_ids: list[UUID] = field(default_factory=list)
    unknown_ids: list[UUID] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def apply(self) -> PedigreeProject:
        return PedigreeProject.model_validate(self.after.model_dump())


class KinshipValidator:
    """Checks graph semantics not covered by Pydantic's referential validation."""

    def validate(self, project: PedigreeProject) -> list[KinshipIssue]:
        issues: list[KinshipIssue] = []
        seen_edges: set[tuple[UUID, UUID, ParentageKind]] = set()
        biological_by_child: dict[UUID, list[UUID]] = {}
        for edge in project.parentages:
            key = (edge.parent_id, edge.child_id, edge.kind)
            if key in seen_edges:
                issues.append(
                    KinshipIssue(
                        KinshipSeverity.ERROR,
                        "duplicate_parentage",
                        "A mesma parentalidade foi registrada mais de uma vez.",
                        (edge.parent_id, edge.child_id),
                    )
                )
            seen_edges.add(key)
            if edge.kind == ParentageKind.BIOLOGICAL:
                biological_by_child.setdefault(edge.child_id, []).append(edge.parent_id)
        for child_id, parent_ids in biological_by_child.items():
            if len(set(parent_ids)) > 2:
                issues.append(
                    KinshipIssue(
                        KinshipSeverity.ERROR,
                        "too_many_biological_parents",
                        "Há mais de dois genitores biológicos registrados para o indivíduo.",
                        (child_id, *parent_ids),
                    )
                )
        pairs: set[frozenset[UUID]] = set()
        for assertion in project.declared_kinships:
            pair = frozenset((assertion.member_a, assertion.member_b))
            marker = (pair, assertion.kind)
            if marker in pairs:
                issues.append(
                    KinshipIssue(
                        KinshipSeverity.ERROR,
                        "duplicate_declared_kinship",
                        "O parentesco declarado está duplicado.",
                        (assertion.member_a, assertion.member_b),
                    )
                )
            pairs.add(marker)
        try:
            PedigreeProject.model_validate(project.model_dump())
        except ValidationError as error:
            issues.append(KinshipIssue(KinshipSeverity.ERROR, "invalid_graph", str(error)))
        return issues

    def require_valid(self, project: PedigreeProject) -> None:
        errors = [
            issue for issue in self.validate(project) if issue.severity == KinshipSeverity.ERROR
        ]
        if errors:
            raise ValueError(errors[0].message)


class KinshipEngine:
    """Source-of-truth service for biological and declared family relationships."""

    def __init__(self, validator: KinshipValidator | None = None) -> None:
        self.validator = validator or KinshipValidator()

    @staticmethod
    def parents(
        project: PedigreeProject,
        person_id: UUID,
        kinds: set[ParentageKind] | None = None,
    ) -> list[UUID]:
        return [
            edge.parent_id
            for edge in project.parentages
            if edge.child_id == person_id and (kinds is None or edge.kind in kinds)
        ]

    @staticmethod
    def children(
        project: PedigreeProject,
        person_id: UUID,
        kinds: set[ParentageKind] | None = None,
    ) -> list[UUID]:
        return [
            edge.child_id
            for edge in project.parentages
            if edge.parent_id == person_id and (kinds is None or edge.kind in kinds)
        ]

    def ancestors(self, project: PedigreeProject, person_id: UUID) -> dict[UUID, int]:
        return self._walk(project, person_id, upward=True)

    def descendants(self, project: PedigreeProject, person_id: UUID) -> dict[UUID, int]:
        return self._walk(project, person_id, upward=False)

    def _walk(self, project: PedigreeProject, person_id: UUID, upward: bool) -> dict[UUID, int]:
        self._person(project, person_id)
        found: dict[UUID, int] = {}
        frontier = [(person_id, 0)]
        while frontier:
            current, distance = frontier.pop(0)
            adjacent = self.parents(project, current) if upward else self.children(project, current)
            for other in adjacent:
                next_distance = distance + 1
                if other not in found or next_distance < found[other]:
                    found[other] = next_distance
                    frontier.append((other, next_distance))
        return found

    def sibling_kind(
        self, project: PedigreeProject, first_id: UUID, second_id: UUID
    ) -> SiblingKind | None:
        self._person(project, first_id)
        self._person(project, second_id)
        declared = next(
            (
                item
                for item in project.declared_kinships
                if {item.member_a, item.member_b} == {first_id, second_id}
            ),
            None,
        )
        if declared:
            return {
                DeclaredKinshipKind.SIBLING_UNRESOLVED: SiblingKind.UNRESOLVED,
                DeclaredKinshipKind.ADOPTIVE_SIBLING: SiblingKind.ADOPTIVE,
                DeclaredKinshipKind.SOCIAL_SIBLING: SiblingKind.SOCIAL,
            }[declared.kind]
        biological = {ParentageKind.BIOLOGICAL}
        first = set(self.parents(project, first_id, biological))
        second = set(self.parents(project, second_id, biological))
        shared = first & second
        if len(shared) >= 2 and first == second:
            return SiblingKind.FULL
        if len(shared) != 1:
            return None
        parent = self._person(project, next(iter(shared)))
        if parent.gender_identity == GenderIdentity.MAN:
            return SiblingKind.PATERNAL_HALF
        if parent.gender_identity == GenderIdentity.WOMAN:
            return SiblingKind.MATERNAL_HALF
        return SiblingKind.UNRESOLVED

    def plan_sibling(
        self,
        project: PedigreeProject,
        person_id: UUID,
        kind: SiblingKind,
        *,
        label: str | None = None,
        other_parent_id: UUID | None = None,
        create_missing_parents: bool = True,
    ) -> KinshipPlan:
        """Plan a sibling without mutating ``project`` or inventing partnerships."""
        source = self._person(project, person_id)
        after = project.model_copy(deep=True)
        sibling = Individual(label=label or self._next_label(after))
        after.individuals.append(sibling)
        plan = KinshipPlan(f"Adicionar {kind.value}", project.model_copy(deep=True), after)
        plan.created_ids.append(sibling.id)

        if kind in {SiblingKind.UNRESOLVED, SiblingKind.ADOPTIVE, SiblingKind.SOCIAL}:
            declared_kind = {
                SiblingKind.UNRESOLVED: DeclaredKinshipKind.SIBLING_UNRESOLVED,
                SiblingKind.ADOPTIVE: DeclaredKinshipKind.ADOPTIVE_SIBLING,
                SiblingKind.SOCIAL: DeclaredKinshipKind.SOCIAL_SIBLING,
            }[kind]
            after.declared_kinships.append(
                DeclaredKinship(
                    member_a=person_id,
                    member_b=sibling.id,
                    kind=declared_kind,
                    evidence_status=EvidenceStatus.CONFIRMED,
                    provenance="sibling assistant",
                )
            )
            plan.notes.append("Parentesco declarado sem inferir ancestralidade biológica.")
            self.validator.require_valid(after)
            return plan

        source_parents = [
            edge
            for edge in after.parentages
            if edge.child_id == person_id and edge.kind == ParentageKind.BIOLOGICAL
        ]
        required_gender = None
        if kind == SiblingKind.PATERNAL_HALF:
            required_gender = GenderIdentity.MAN
        elif kind == SiblingKind.MATERNAL_HALF:
            required_gender = GenderIdentity.WOMAN

        if kind == SiblingKind.FULL:
            shared_edges = source_parents
            if len(shared_edges) < 2:
                if not create_missing_parents:
                    raise ValueError("os dois genitores biológicos precisam ser definidos")
                while len(shared_edges) < 2:
                    genders = {
                        self._person(after, edge.parent_id).gender_identity for edge in shared_edges
                    }
                    gender = (
                        GenderIdentity.MAN
                        if GenderIdentity.MAN not in genders
                        else GenderIdentity.WOMAN
                    )
                    parent = self._unknown(
                        after, f"genitor compartilhado de {source.label}", gender
                    )
                    after.individuals.append(parent)
                    edge = Parentage(
                        parent_id=parent.id,
                        child_id=person_id,
                        kind=ParentageKind.BIOLOGICAL,
                        evidence_status=EvidenceStatus.PROVISIONAL,
                        provenance="sibling assistant",
                    )
                    after.parentages.append(edge)
                    shared_edges.append(edge)
                    plan.created_ids.append(parent.id)
                    plan.unknown_ids.append(parent.id)
            for edge in shared_edges[:2]:
                after.parentages.append(
                    Parentage(
                        parent_id=edge.parent_id,
                        child_id=sibling.id,
                        kind=ParentageKind.BIOLOGICAL,
                        evidence_status=edge.evidence_status,
                        provenance="sibling assistant",
                    )
                )
                plan.reused_ids.append(edge.parent_id)
        else:
            candidates = [
                edge
                for edge in source_parents
                if self._person(after, edge.parent_id).gender_identity == required_gender
            ]
            if len(candidates) != 1:
                relation = "pai" if required_gender == GenderIdentity.MAN else "mãe"
                raise ValueError(f"defina exatamente um {relation} biológico compartilhado")
            shared = candidates[0]
            after.parentages.append(
                Parentage(
                    parent_id=shared.parent_id,
                    child_id=sibling.id,
                    kind=ParentageKind.BIOLOGICAL,
                    evidence_status=shared.evidence_status,
                    provenance="sibling assistant",
                )
            )
            plan.reused_ids.append(shared.parent_id)
            if other_parent_id is not None:
                self._person(after, other_parent_id)
                source_other = {
                    edge.parent_id for edge in source_parents if edge.parent_id != shared.parent_id
                }
                if other_parent_id in source_other:
                    raise ValueError(
                        "o outro genitor deve ser diferente do genitor do indivíduo de referência"
                    )
                after.parentages.append(
                    Parentage(
                        parent_id=other_parent_id,
                        child_id=sibling.id,
                        kind=ParentageKind.BIOLOGICAL,
                        provenance="sibling assistant",
                    )
                )
                plan.reused_ids.append(other_parent_id)
            elif create_missing_parents:
                other_gender = (
                    GenderIdentity.WOMAN
                    if required_gender == GenderIdentity.MAN
                    else GenderIdentity.MAN
                )
                unknown = self._unknown(
                    after,
                    f"genitor diferente do meio-irmão de {source.label}",
                    other_gender,
                )
                after.individuals.append(unknown)
                after.parentages.append(
                    Parentage(
                        parent_id=unknown.id,
                        child_id=sibling.id,
                        kind=ParentageKind.BIOLOGICAL,
                        evidence_status=EvidenceStatus.PROVISIONAL,
                        provenance="sibling assistant: confirmed different parent",
                    )
                )
                plan.created_ids.append(unknown.id)
                plan.unknown_ids.append(unknown.id)
        self.validator.require_valid(after)
        return plan

    def reconcile_unknown(
        self, project: PedigreeProject, unknown_id: UUID, existing_id: UUID
    ) -> KinshipPlan:
        unknown = self._person(project, unknown_id)
        self._person(project, existing_id)
        if not unknown.placeholder:
            raise ValueError("o indivíduo de origem não é um representante desconhecido")
        if unknown_id == existing_id:
            raise ValueError("selecione dois indivíduos distintos")
        after_data = project.model_dump()
        for edge in after_data["parentages"]:
            if edge["parent_id"] == unknown_id:
                edge["parent_id"] = existing_id
            if edge["child_id"] == unknown_id:
                edge["child_id"] = existing_id
        for relation in after_data["relationships"]:
            if relation["member_a"] == unknown_id:
                relation["member_a"] = existing_id
            if relation["member_b"] == unknown_id:
                relation["member_b"] = existing_id
        for assertion in after_data["declared_kinships"]:
            if assertion["member_a"] == unknown_id:
                assertion["member_a"] = existing_id
            if assertion["member_b"] == unknown_id:
                assertion["member_b"] = existing_id
        after_data["individuals"] = [
            person for person in after_data["individuals"] if person["id"] != unknown_id
        ]
        after = PedigreeProject.model_validate(after_data)
        self.validator.require_valid(after)
        return KinshipPlan(
            "Reconciliar familiar desconhecido",
            project.model_copy(deep=True),
            after,
            reused_ids=[existing_id],
            notes=["O representante desconhecido será substituído após validação."],
        )

    @staticmethod
    def _person(project: PedigreeProject, person_id: UUID) -> Individual:
        person = next((item for item in project.individuals if item.id == person_id), None)
        if person is None:
            raise ValueError("individual is absent from the project")
        return person

    @staticmethod
    def _next_label(project: PedigreeProject) -> str:
        return f"P-{len(project.individuals) + 1}"

    @staticmethod
    def _unknown(project: PedigreeProject, reason: str, gender: GenderIdentity) -> Individual:
        return Individual(
            label="Desconhecido",
            gender_identity=gender,
            placeholder=True,
            unknown_reason=reason,
            provenance="kinship engine",
        )
