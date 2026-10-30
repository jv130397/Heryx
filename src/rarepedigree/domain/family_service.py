"""Pure family graph mutations used by UI commands and tests."""

from __future__ import annotations

from uuid import UUID

from rarepedigree.domain.models import (
    GenderIdentity,
    Individual,
    Parentage,
    ParentageKind,
    PedigreeProject,
    Relationship,
    TwinGroup,
    TwinZygosity,
)


class FamilyService:
    @staticmethod
    def set_twins(
        project: PedigreeProject, member_ids: list[UUID], zygosity: TwinZygosity
    ) -> PedigreeProject:
        if len(set(member_ids)) < 2:
            raise ValueError("select at least two distinct individuals")
        updated = project.model_copy(deep=True)
        for person_id in member_ids:
            _person(updated, person_id)
        parent_sets = [
            {edge.parent_id for edge in updated.parentages if edge.child_id == person_id}
            for person_id in member_ids
        ]
        if not parent_sets[0] or any(
            parent_set != parent_sets[0] for parent_set in parent_sets[1:]
        ):
            raise ValueError("twins must share the same recorded parents")
        updated.twin_groups = [
            group
            for group in updated.twin_groups
            if not set(group.member_ids).intersection(member_ids)
        ]
        updated.twin_groups.append(TwinGroup(member_ids=member_ids, zygosity=zygosity))
        return _validated(updated)

    @staticmethod
    def add_partner(project: PedigreeProject, person_id: UUID) -> tuple[PedigreeProject, UUID]:
        updated = project.model_copy(deep=True)
        person = _person(updated, person_id)
        partner_gender = (
            GenderIdentity.WOMAN
            if person.gender_identity == GenderIdentity.MAN
            else GenderIdentity.MAN
            if person.gender_identity == GenderIdentity.WOMAN
            else GenderIdentity.UNKNOWN
        )
        partner = Individual(label=_next_label(updated), gender_identity=partner_gender)
        updated.individuals.append(partner)
        updated.relationships.append(Relationship(member_a=person_id, member_b=partner.id))
        return _validated(updated), partner.id

    @staticmethod
    def add_child(
        project: PedigreeProject,
        parent_id: UUID,
        partner_id: UUID | None = None,
        kind: ParentageKind = ParentageKind.BIOLOGICAL,
    ) -> tuple[PedigreeProject, UUID]:
        updated = project.model_copy(deep=True)
        _person(updated, parent_id)
        if partner_id is not None:
            _person(updated, partner_id)
        child = Individual(label=_next_label(updated), gender_identity=GenderIdentity.UNKNOWN)
        updated.individuals.append(child)
        updated.parentages.append(Parentage(parent_id=parent_id, child_id=child.id, kind=kind))
        if partner_id is not None:
            updated.parentages.append(
                Parentage(parent_id=partner_id, child_id=child.id, kind=kind)
            )
        return _validated(updated), child.id

    @staticmethod
    def add_parents(
        project: PedigreeProject, child_id: UUID, unknown: bool = False
    ) -> tuple[PedigreeProject, tuple[UUID, UUID]]:
        updated = project.model_copy(deep=True)
        _person(updated, child_id)
        if any(edge.child_id == child_id for edge in updated.parentages):
            raise ValueError("the selected individual already has recorded parents")
        parent_a = Individual(
            label=_next_label(updated),
            gender_identity=GenderIdentity.UNKNOWN if unknown else GenderIdentity.MAN,
            placeholder=unknown,
        )
        updated.individuals.append(parent_a)
        parent_b = Individual(
            label=_next_label(updated),
            gender_identity=GenderIdentity.UNKNOWN if unknown else GenderIdentity.WOMAN,
            placeholder=unknown,
        )
        updated.individuals.append(parent_b)
        updated.relationships.append(Relationship(member_a=parent_a.id, member_b=parent_b.id))
        kind = ParentageKind.UNKNOWN if unknown else ParentageKind.BIOLOGICAL
        updated.parentages.extend(
            [
                Parentage(parent_id=parent_a.id, child_id=child_id, kind=kind),
                Parentage(parent_id=parent_b.id, child_id=child_id, kind=kind),
            ]
        )
        return _validated(updated), (parent_a.id, parent_b.id)

    @staticmethod
    def add_sibling(project: PedigreeProject, person_id: UUID) -> tuple[PedigreeProject, UUID]:
        updated = project.model_copy(deep=True)
        _person(updated, person_id)
        parent_edges = [edge for edge in updated.parentages if edge.child_id == person_id]
        if not parent_edges:
            updated, _ = FamilyService.add_parents(updated, person_id)
            parent_edges = [edge for edge in updated.parentages if edge.child_id == person_id]
        sibling = Individual(label=_next_label(updated), gender_identity=GenderIdentity.UNKNOWN)
        updated.individuals.append(sibling)
        for edge in parent_edges:
            updated.parentages.append(
                Parentage(parent_id=edge.parent_id, child_id=sibling.id, kind=edge.kind)
            )
        return _validated(updated), sibling.id

    @staticmethod
    def delete_individual(project: PedigreeProject, person_id: UUID) -> PedigreeProject:
        updated = project.model_copy(deep=True)
        _person(updated, person_id)
        data = updated.model_dump()
        data["relationships"] = [
            item
            for item in data["relationships"]
            if person_id not in {item["member_a"], item["member_b"]}
        ]
        data["parentages"] = [
            edge
            for edge in data["parentages"]
            if person_id not in {edge["parent_id"], edge["child_id"]}
        ]
        data["twin_groups"] = [
            {**group, "member_ids": [item for item in group["member_ids"] if item != person_id]}
            for group in data["twin_groups"]
            if len([item for item in group["member_ids"] if item != person_id]) >= 2
        ]
        data["individuals"] = [
            person for person in data["individuals"] if person["id"] != person_id
        ]
        return PedigreeProject.model_validate(data)


def _person(project: PedigreeProject, person_id: UUID) -> Individual:
    for person in project.individuals:
        if person.id == person_id:
            return person
    raise ValueError("individual is absent from the project")


def _next_label(project: PedigreeProject) -> str:
    return f"P-{len(project.individuals) + 1}"


def _validated(project: PedigreeProject) -> PedigreeProject:
    return PedigreeProject.model_validate(project.model_dump())
