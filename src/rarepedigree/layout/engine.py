"""Qt-independent multigenerational pedigree layout."""

from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from rarepedigree.domain import PedigreeProject


class PedigreeLayoutEngine:
    HORIZONTAL_SPACING = 130.0
    FAMILY_GAP = 220.0
    VERTICAL_SPACING = 180.0

    def generations(self, project: PedigreeProject) -> dict[UUID, int]:
        generation = {person.id: 0 for person in project.individuals}
        # Parentage establishes vertical levels. Partnerships then pull both
        # members onto the same level and the constraints are propagated again.
        # The bounded fixed-point keeps malformed cross-generation partnerships
        # from hanging the editor while producing stable normal pedigrees.
        limit = max(1, len(project.individuals) * 2)
        for _ in range(limit):
            changed = False
            for relation in project.relationships:
                shared = max(generation[relation.member_a], generation[relation.member_b])
                if generation[relation.member_a] != shared:
                    generation[relation.member_a] = shared
                    changed = True
                if generation[relation.member_b] != shared:
                    generation[relation.member_b] = shared
                    changed = True
            parents_by_child: dict[UUID, list[UUID]] = defaultdict(list)
            for edge in project.parentages:
                parents_by_child[edge.child_id].append(edge.parent_id)
            for parent_ids in parents_by_child.values():
                shared = max(generation[parent_id] for parent_id in parent_ids)
                for parent_id in parent_ids:
                    if generation[parent_id] != shared:
                        generation[parent_id] = shared
                        changed = True
            for edge in project.parentages:
                candidate = generation[edge.parent_id] + 1
                if generation[edge.child_id] < candidate:
                    generation[edge.child_id] = candidate
                    changed = True
                elif generation[edge.child_id] > candidate:
                    # A deeper ancestry on the co-parent's side may already
                    # have moved the child down. Pull this parent's entire
                    # branch down as well so no edge skips a generation.
                    generation[edge.parent_id] = generation[edge.child_id] - 1
                    changed = True
            if not changed:
                break
        minimum = min(generation.values(), default=0)
        if minimum:
            generation = {person_id: level - minimum for person_id, level in generation.items()}
        return generation

    def compute(
        self, project: PedigreeProject, preserve_locked: bool = True
    ) -> dict[UUID, tuple[float, float]]:
        generations = self.generations(project)
        levels: dict[int, list[UUID]] = defaultdict(list)
        for person in project.individuals:
            levels[generations[person.id]].append(person.id)
        people = {person.id: person for person in project.individuals}
        parents: dict[UUID, list[UUID]] = defaultdict(list)
        children: dict[UUID, list[UUID]] = defaultdict(list)
        for edge in project.parentages:
            parents[edge.child_id].append(edge.parent_id)
            children[edge.parent_id].append(edge.child_id)

        units_by_level = {
            level: self._family_units(project, members) for level, members in levels.items()
        }
        for units in units_by_level.values():
            units.sort(
                key=lambda unit: (
                    sum(people[person_id].layout.x for person_id in unit) / len(unit),
                    min(people[person_id].label for person_id in unit),
                )
            )

        def ranks() -> dict[UUID, float]:
            result: dict[UUID, float] = {}
            for level in sorted(units_by_level):
                cursor = 0.0
                for unit in units_by_level[level]:
                    for offset, person_id in enumerate(unit):
                        result[person_id] = cursor + offset
                    cursor += len(unit) + 1.0
            return result

        # Alternating barycentric sweeps are the standard layered-graph step
        # that prevents ancestry branches from being ordered by UUID/addition
        # order. Partnership components remain indivisible during each sweep.
        for _ in range(8):
            current = ranks()
            for level in sorted(units_by_level)[1:]:
                previous_order = {
                    id(unit): index for index, unit in enumerate(units_by_level[level])
                }
                units_by_level[level].sort(
                    key=lambda unit: self._barycenter_key(
                        unit, parents, current, previous_order[id(unit)]
                    )
                )
            current = ranks()
            for level in sorted(units_by_level, reverse=True)[1:]:
                previous_order = {
                    id(unit): index for index, unit in enumerate(units_by_level[level])
                }
                units_by_level[level].sort(
                    key=lambda unit: self._barycenter_key(
                        unit, children, current, previous_order[id(unit)]
                    )
                )

        # If one member of a partnership belongs to a sibship, keep that
        # member on the side facing their siblings. Otherwise the partner can
        # be placed between siblings and appear to be their biological sibling.
        biological_parent_sets = {
            person_id: frozenset(parents[person_id]) for person_id in generations
        }
        for units in units_by_level.values():
            unit_index = {
                person_id: index for index, unit in enumerate(units) for person_id in unit
            }
            for index, unit in enumerate(units):
                anchors = [person_id for person_id in unit if biological_parent_sets[person_id]]
                if len(anchors) != 1:
                    continue
                anchor = anchors[0]
                sibling_indices = [
                    unit_index[other]
                    for other, parent_set in biological_parent_sets.items()
                    if other not in unit
                    and parent_set == biological_parent_sets[anchor]
                    and other in unit_index
                ]
                if not sibling_indices:
                    continue
                partners = [person_id for person_id in unit if person_id != anchor]
                unit[:] = (
                    [*partners, anchor]
                    if sum(sibling_indices) / len(sibling_indices) > index
                    else [anchor, *partners]
                )

        positions: dict[UUID, tuple[float, float]] = {}
        for level in sorted(units_by_level):
            units = units_by_level[level]
            total_width = (
                sum((len(unit) - 1) * self.HORIZONTAL_SPACING for unit in units)
                + max(0, len(units) - 1) * self.FAMILY_GAP
            )
            cursor = -total_width / 2
            provisional: dict[UUID, float] = {}
            for unit in units:
                unit_width = (len(unit) - 1) * self.HORIZONTAL_SPACING
                for index, person_id in enumerate(unit):
                    provisional[person_id] = cursor + index * self.HORIZONTAL_SPACING
                cursor += unit_width + self.FAMILY_GAP
            for person_id in levels[level]:
                person = people[person_id]
                if preserve_locked and person.layout.locked:
                    positions[person_id] = (person.layout.x, person.layout.y)
                else:
                    positions[person_id] = (
                        provisional[person_id],
                        level * self.VERTICAL_SPACING,
                    )
        return positions

    @staticmethod
    def _barycenter_key(
        unit: list[UUID],
        neighbours: dict[UUID, list[UUID]],
        ranks: dict[UUID, float],
        fallback: int,
    ) -> tuple[float, int]:
        connected = [
            ranks[other] for person_id in unit for other in neighbours[person_id] if other in ranks
        ]
        return (
            sum(connected) / len(connected) if connected else float(fallback),
            fallback,
        )

    @staticmethod
    def _family_units(project: PedigreeProject, members: list[UUID]) -> list[list[UUID]]:
        """Return reproductive-family components without inventing partnerships.

        Co-parents must remain visually close even when no affective/conjugal
        relationship is known. Their parentage edges provide layout adjacency,
        but remain scientifically distinct from ``Relationship`` records.
        """
        member_set = set(members)
        neighbours: dict[UUID, set[UUID]] = {person_id: set() for person_id in members}
        for relation in project.relationships:
            if relation.member_a in member_set and relation.member_b in member_set:
                neighbours[relation.member_a].add(relation.member_b)
                neighbours[relation.member_b].add(relation.member_a)
        parents_by_child: dict[UUID, list[UUID]] = defaultdict(list)
        for edge in project.parentages:
            if edge.parent_id in member_set:
                parents_by_child[edge.child_id].append(edge.parent_id)
        for parent_ids in parents_by_child.values():
            for index, first in enumerate(parent_ids):
                for second in parent_ids[index + 1 :]:
                    neighbours[first].add(second)
                    neighbours[second].add(first)
        people = {person.id: person for person in project.individuals}
        gender_rank = {"man": 0, "unknown": 1, "gender_diverse": 1, "woman": 2}
        remaining = set(members)
        units = []
        while remaining:
            seed = min(remaining, key=str)
            stack = [seed]
            component = set()
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                component.add(current)
                stack.extend(neighbours[current] - component)
            remaining -= component
            units.append(
                sorted(
                    component,
                    key=lambda person_id: (
                        gender_rank[people[person_id].gender_identity.value],
                        people[person_id].label,
                        str(person_id),
                    ),
                )
            )
        return units
