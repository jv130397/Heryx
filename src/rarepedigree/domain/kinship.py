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
            derived = KinshipEngine()._biological_sibling_kind(
                project, assertion.member_a, assertion.member_b
            )
            if derived is not None:
                issues.append(
                    KinshipIssue(
                        KinshipSeverity.AMBIGUITY,
                        "declared_kinship_has_biological_path",
                        "O parentesco declarado já possui um caminho biológico "
                        "que deve ser revisado.",
                        (assertion.member_a, assertion.member_b),
                    )
                )
        seen_relationships: set[tuple[frozenset[UUID], object]] = set()
        for relation in project.relationships:
            marker = (frozenset((relation.member_a, relation.member_b)), relation.kind)
            if marker in seen_relationships:
                issues.append(
                    KinshipIssue(
                        KinshipSeverity.ERROR,
                        "duplicate_relationship",
                        "A mesma relação foi registrada mais de uma vez.",
                        (relation.member_a, relation.member_b),
                    )
                )
            seen_relationships.add(marker)
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
        return self._biological_sibling_kind(project, first_id, second_id)

    def _biological_sibling_kind(
        self, project: PedigreeProject, first_id: UUID, second_id: UUID
    ) -> SiblingKind | None:
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

    def plan_change_sibling_kind(
        self,
        project: PedigreeProject,
        first_id: UUID,
        second_id: UUID,
        new_kind: SiblingKind,
    ) -> KinshipPlan:
        """Replace only the second person's sibling-defining incoming edges."""
        self._person(project, first_id)
        self._person(project, second_id)
        new_kind = SiblingKind(new_kind)
        after = project.model_copy(deep=True)
        affected = [
            edge
            for edge in after.parentages
            if edge.child_id == second_id and edge.kind == ParentageKind.BIOLOGICAL
        ]
        after.parentages = [
            edge
            for edge in after.parentages
            if not (edge.child_id == second_id and edge.kind == ParentageKind.BIOLOGICAL)
        ]
        after.declared_kinships = [
            item
            for item in after.declared_kinships
            if {item.member_a, item.member_b} != {first_id, second_id}
        ]
        plan = KinshipPlan(
            "Alterar tipo de irmandade",
            project.model_copy(deep=True),
            after,
            notes=[
                f"{len(affected)} parentalidade(s) biológica(s) do segundo "
                "indivíduo serão substituídas."
            ],
        )
        if new_kind in {SiblingKind.UNRESOLVED, SiblingKind.ADOPTIVE, SiblingKind.SOCIAL}:
            declared_kind = {
                SiblingKind.UNRESOLVED: DeclaredKinshipKind.SIBLING_UNRESOLVED,
                SiblingKind.ADOPTIVE: DeclaredKinshipKind.ADOPTIVE_SIBLING,
                SiblingKind.SOCIAL: DeclaredKinshipKind.SOCIAL_SIBLING,
            }[new_kind]
            after.declared_kinships.append(
                DeclaredKinship(
                    member_a=first_id,
                    member_b=second_id,
                    kind=declared_kind,
                    provenance="kinship relationship editor",
                )
            )
        else:
            first_edges = [
                edge
                for edge in after.parentages
                if edge.child_id == first_id and edge.kind == ParentageKind.BIOLOGICAL
            ]
            if new_kind == SiblingKind.FULL:
                if len(first_edges) != 2:
                    raise ValueError(
                        "o indivíduo de referência precisa ter dois genitores definidos"
                    )
                shared = first_edges
            else:
                required = (
                    GenderIdentity.MAN
                    if new_kind == SiblingKind.PATERNAL_HALF
                    else GenderIdentity.WOMAN
                )
                shared = [
                    edge
                    for edge in first_edges
                    if self._person(after, edge.parent_id).gender_identity == required
                ]
                if len(shared) != 1:
                    raise ValueError("o genitor compartilhado não está definido sem ambiguidade")
            for edge in shared:
                after.parentages.append(
                    Parentage(
                        parent_id=edge.parent_id,
                        child_id=second_id,
                        kind=ParentageKind.BIOLOGICAL,
                        evidence_status=edge.evidence_status,
                        provenance="kinship relationship editor",
                    )
                )
                plan.reused_ids.append(edge.parent_id)
            if new_kind in {SiblingKind.PATERNAL_HALF, SiblingKind.MATERNAL_HALF}:
                other_gender = (
                    GenderIdentity.WOMAN
                    if new_kind == SiblingKind.PATERNAL_HALF
                    else GenderIdentity.MAN
                )
                unknown = self._unknown(
                    after,
                    "genitor diferente criado pela edição de irmandade",
                    other_gender,
                )
                after.individuals.append(unknown)
                after.parentages.append(
                    Parentage(
                        parent_id=unknown.id,
                        child_id=second_id,
                        kind=ParentageKind.BIOLOGICAL,
                        evidence_status=EvidenceStatus.PROVISIONAL,
                        provenance="kinship relationship editor",
                    )
                )
                plan.created_ids.append(unknown.id)
                plan.unknown_ids.append(unknown.id)
        self.validator.require_valid(after)
        plan.after = after
        return plan

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
        kind = SiblingKind(kind)
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

    def plan_child(
        self,
        project: PedigreeProject,
        parent_id: UUID,
        *,
        coparent_id: UUID | None = None,
        label: str | None = None,
        kind: ParentageKind = ParentageKind.BIOLOGICAL,
        create_unknown_coparent: bool = True,
    ) -> KinshipPlan:
        """Plan a child and supply a traceable unknown co-parent when safe.

        A reproductive co-parent is not recorded as a partnership. For an
        unspecified/diverse selected parent, the missing co-parent's sex also
        remains unspecified instead of manufacturing a binary fact.
        """
        source = self._person(project, parent_id)
        after = project.model_copy(deep=True)
        child = Individual(label=label or self._next_label(after))
        after.individuals.append(child)
        plan = KinshipPlan("Adicionar filho", project.model_copy(deep=True), after)
        plan.created_ids.append(child.id)
        after.parentages.append(
            Parentage(
                parent_id=parent_id,
                child_id=child.id,
                kind=kind,
                evidence_status=EvidenceStatus.CONFIRMED,
                provenance="child assistant",
            )
        )
        if coparent_id is not None:
            self._person(after, coparent_id)
            if coparent_id == parent_id:
                raise ValueError("o outro genitor deve ser um indivíduo diferente")
            after.parentages.append(
                Parentage(
                    parent_id=coparent_id,
                    child_id=child.id,
                    kind=kind,
                    evidence_status=EvidenceStatus.CONFIRMED,
                    provenance="child assistant",
                )
            )
            plan.reused_ids.append(coparent_id)
        elif create_unknown_coparent and kind == ParentageKind.BIOLOGICAL:
            gender = {
                GenderIdentity.MAN: GenderIdentity.WOMAN,
                GenderIdentity.WOMAN: GenderIdentity.MAN,
            }.get(source.gender_identity, GenderIdentity.UNKNOWN)
            relation = {
                GenderIdentity.WOMAN: "mãe biológica não identificada",
                GenderIdentity.MAN: "pai biológico não identificado",
            }.get(gender, "outro genitor biológico não identificado")
            unknown = self._unknown(after, f"{relation} de {child.label}", gender)
            after.individuals.append(unknown)
            after.parentages.append(
                Parentage(
                    parent_id=unknown.id,
                    child_id=child.id,
                    kind=ParentageKind.BIOLOGICAL,
                    evidence_status=EvidenceStatus.PROVISIONAL,
                    provenance="child assistant: automatically created missing co-parent",
                )
            )
            plan.created_ids.append(unknown.id)
            plan.unknown_ids.append(unknown.id)
            plan.notes.append(
                "Genitor biológico desconhecido criado sem inferir parceria ou casamento."
            )
        self.validator.require_valid(after)
        return plan

    def plan_ancestor_path(
        self,
        project: PedigreeProject,
        person_id: UUID,
        path: list[GenderIdentity],
        *,
        label: str | None = None,
        create_missing_intermediates: bool = True,
    ) -> KinshipPlan:
        """Add/reuse an ancestor using an unambiguous upward path.

        ``[WOMAN, MAN]`` means mother followed by maternal grandfather.
        Only the final ancestor is identified; missing intermediate people are
        structural unknowns with stable UUIDs and provenance.
        """
        if not path:
            raise ValueError("o caminho ancestral não pode estar vazio")
        self._person(project, person_id)
        after = project.model_copy(deep=True)
        plan = KinshipPlan("Adicionar ascendente", project.model_copy(deep=True), after)
        current_id = person_id
        for index, gender in enumerate(path):
            is_final = index == len(path) - 1
            candidates = [
                edge.parent_id
                for edge in after.parentages
                if edge.child_id == current_id
                and edge.kind == ParentageKind.BIOLOGICAL
                and self._person(after, edge.parent_id).gender_identity == gender
            ]
            if len(candidates) > 1:
                raise ValueError("há mais de um ascendente possível neste ramo")
            if candidates:
                current_id = candidates[0]
                plan.reused_ids.append(current_id)
                if is_final and label:
                    raise ValueError("o ascendente já existe; edite ou reconcilie o indivíduo")
                continue
            if not is_final and not create_missing_intermediates:
                raise ValueError("o caminho exige um familiar intermediário ainda ausente")
            if is_final:
                ancestor = Individual(
                    label=label or self._next_label(after),
                    gender_identity=gender,
                    provenance="kinship ancestor assistant",
                )
            else:
                ancestor = self._unknown(
                    after,
                    f"intermediário ancestral no nível {index + 1}",
                    gender,
                )
            after.individuals.append(ancestor)
            after.parentages.append(
                Parentage(
                    parent_id=ancestor.id,
                    child_id=current_id,
                    kind=ParentageKind.BIOLOGICAL,
                    evidence_status=(
                        EvidenceStatus.CONFIRMED if is_final else EvidenceStatus.PROVISIONAL
                    ),
                    provenance="kinship ancestor assistant",
                )
            )
            plan.created_ids.append(ancestor.id)
            if ancestor.placeholder:
                plan.unknown_ids.append(ancestor.id)
            current_id = ancestor.id
        plan.notes.append("Caminho ancestral: " + " → ".join(item.value for item in path))
        self.validator.require_valid(after)
        return plan

    def plan_descendant(
        self,
        project: PedigreeProject,
        person_id: UUID,
        generations: int,
        *,
        label: str | None = None,
        gender: GenderIdentity = GenderIdentity.UNKNOWN,
        create_missing_intermediates: bool = True,
    ) -> KinshipPlan:
        """Plan child/grandchild/great-grandchild as one atomic operation."""
        if generations < 1:
            raise ValueError("a distância do descendente deve ser positiva")
        if generations > 1 and not create_missing_intermediates:
            raise ValueError("o caminho descendente exige familiares intermediários")
        self._person(project, person_id)
        after = project.model_copy(deep=True)
        combined = KinshipPlan("Adicionar descendente", project.model_copy(deep=True), after)
        current_id = person_id
        for depth in range(1, generations + 1):
            is_final = depth == generations
            if not is_final and not create_missing_intermediates:
                raise ValueError("o descendente exige um familiar intermediário ausente")
            step = self.plan_child(
                after,
                current_id,
                label=label if is_final else "Desconhecido",
            )
            after = step.apply()
            child_id = step.created_ids[0]
            child = self._person(after, child_id)
            if is_final:
                child.gender_identity = gender
            else:
                child.placeholder = True
                child.unknown_reason = f"descendente intermediário no nível {depth}"
                child.provenance = "kinship descendant assistant"
                combined.unknown_ids.append(child_id)
            combined.created_ids.extend(step.created_ids)
            combined.unknown_ids.extend(
                item for item in step.unknown_ids if item not in combined.unknown_ids
            )
            current_id = child_id
        combined.after = PedigreeProject.model_validate(after.model_dump())
        self.validator.require_valid(combined.after)
        return combined

    def plan_aunt_uncle(
        self,
        project: PedigreeProject,
        person_id: UUID,
        *,
        branch_gender: GenderIdentity,
        relative_gender: GenderIdentity,
        sibling_kind: SiblingKind = SiblingKind.FULL,
        label: str | None = None,
        create_missing_intermediates: bool = True,
    ) -> KinshipPlan:
        """Plan an aunt/uncle through the explicitly selected parental branch."""
        parent_plan = self.plan_ancestor_path(
            project,
            person_id,
            [branch_gender],
            create_missing_intermediates=create_missing_intermediates,
        )
        after = parent_plan.apply()
        branch_parent = next(
            edge.parent_id
            for edge in after.parentages
            if edge.child_id == person_id
            and self._person(after, edge.parent_id).gender_identity == branch_gender
        )
        if branch_parent in parent_plan.created_ids:
            structural_parent = self._person(after, branch_parent)
            structural_parent.placeholder = True
            structural_parent.unknown_reason = "genitor intermediário para parentesco colateral"
            structural_parent.provenance = "kinship collateral assistant"
            if branch_parent not in parent_plan.unknown_ids:
                parent_plan.unknown_ids.append(branch_parent)
            parent_plan.after = after.model_copy(deep=True)
        sibling_plan = self.plan_sibling(
            after,
            branch_parent,
            sibling_kind,
            label=label,
        )
        result = self._combine_plans("Adicionar tio ou tia", project, parent_plan, sibling_plan)
        relative = self._person(result.after, sibling_plan.created_ids[0])
        relative.gender_identity = relative_gender
        result.after = PedigreeProject.model_validate(result.after.model_dump())
        return result

    def plan_cousin(
        self,
        project: PedigreeProject,
        person_id: UUID,
        *,
        branch_gender: GenderIdentity,
        intermediary_gender: GenderIdentity = GenderIdentity.UNKNOWN,
        cousin_gender: GenderIdentity = GenderIdentity.UNKNOWN,
        intermediary_sibling_kind: SiblingKind = SiblingKind.FULL,
        label: str | None = None,
        create_missing_intermediates: bool = True,
    ) -> KinshipPlan:
        aunt_plan = self.plan_aunt_uncle(
            project,
            person_id,
            branch_gender=branch_gender,
            relative_gender=intermediary_gender,
            sibling_kind=intermediary_sibling_kind,
            create_missing_intermediates=create_missing_intermediates,
        )
        intermediary_id = next(
            item
            for item in aunt_plan.created_ids
            if not self._person(aunt_plan.after, item).placeholder
        )
        child_plan = self.plan_child(aunt_plan.after, intermediary_id, label=label)
        result = self._combine_plans("Adicionar primo ou prima", project, aunt_plan, child_plan)
        self._person(result.after, child_plan.created_ids[0]).gender_identity = cousin_gender
        result.after = PedigreeProject.model_validate(result.after.model_dump())
        return result

    def plan_nephew_niece(
        self,
        project: PedigreeProject,
        person_id: UUID,
        *,
        sibling_id: UUID | None = None,
        sibling_kind: SiblingKind = SiblingKind.FULL,
        gender: GenderIdentity = GenderIdentity.UNKNOWN,
        label: str | None = None,
    ) -> KinshipPlan:
        if sibling_id is None:
            sibling_plan = self.plan_sibling(project, person_id, sibling_kind)
            after = sibling_plan.apply()
            sibling_id = sibling_plan.created_ids[0]
            plans = [sibling_plan]
        else:
            self._person(project, sibling_id)
            after = project.model_copy(deep=True)
            plans = []
            if self.sibling_kind(after, person_id, sibling_id) is None:
                raise ValueError("o genitor indicado não é irmão do indivíduo de referência")
        child_plan = self.plan_child(after, sibling_id, label=label)
        plans.append(child_plan)
        result = self._combine_plans("Adicionar sobrinho ou sobrinha", project, *plans)
        self._person(result.after, child_plan.created_ids[0]).gender_identity = gender
        result.after = PedigreeProject.model_validate(result.after.model_dump())
        return result

    @staticmethod
    def _combine_plans(label: str, project: PedigreeProject, *plans: KinshipPlan) -> KinshipPlan:
        if not plans:
            raise ValueError("nenhuma operação foi planejada")
        result = KinshipPlan(
            label,
            project.model_copy(deep=True),
            plans[-1].after.model_copy(deep=True),
        )
        for plan in plans:
            for item in plan.created_ids:
                if item not in result.created_ids:
                    result.created_ids.append(item)
            for item in plan.reused_ids:
                if item not in result.reused_ids:
                    result.reused_ids.append(item)
            for item in plan.unknown_ids:
                if item not in result.unknown_ids:
                    result.unknown_ids.append(item)
            result.notes.extend(plan.notes)
        return result

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
        for group in after_data["twin_groups"]:
            group["member_ids"] = [
                existing_id if item == unknown_id else item for item in group["member_ids"]
            ]
        after_data["individuals"] = [
            person for person in after_data["individuals"] if person["id"] != unknown_id
        ]
        after_data["parentages"] = self._deduplicate_dicts(
            after_data["parentages"], ("parent_id", "child_id", "kind")
        )
        after_data["relationships"] = self._deduplicate_undirected(
            after_data["relationships"], "member_a", "member_b", "kind"
        )
        after_data["declared_kinships"] = self._deduplicate_undirected(
            after_data["declared_kinships"], "member_a", "member_b", "kind"
        )
        for group in after_data["twin_groups"]:
            group["member_ids"] = list(dict.fromkeys(group["member_ids"]))
        after_data["twin_groups"] = [
            group for group in after_data["twin_groups"] if len(group["member_ids"]) >= 2
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
    def _deduplicate_dicts(items: list[dict], keys: tuple[str, ...]) -> list[dict]:
        result = []
        seen = set()
        for item in items:
            marker = tuple(item[key] for key in keys)
            if marker not in seen:
                seen.add(marker)
                result.append(item)
        return result

    @staticmethod
    def _deduplicate_undirected(
        items: list[dict], first_key: str, second_key: str, kind_key: str
    ) -> list[dict]:
        result = []
        seen = set()
        for item in items:
            marker = (frozenset((item[first_key], item[second_key])), item[kind_key])
            if marker not in seen:
                seen.add(marker)
                result.append(item)
        return result

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
