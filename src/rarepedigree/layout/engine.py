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
            for edge in project.parentages:
                candidate = generation[edge.parent_id] + 1
                if generation[edge.child_id] < candidate:
                    generation[edge.child_id] = candidate
                    changed = True
            if not changed:
                break
        return generation

    def compute(
        self, project: PedigreeProject, preserve_locked: bool = True
    ) -> dict[UUID, tuple[float, float]]:
        generations = self.generations(project)
        levels: dict[int, list[UUID]] = defaultdict(list)
        for person in project.individuals:
            levels[generations[person.id]].append(person.id)
        positions: dict[UUID, tuple[float, float]] = {}
        people = {person.id: person for person in project.individuals}
        parent_order = defaultdict(list)
        for edge in project.parentages:
            parent_order[edge.child_id].append(edge.parent_id)
        for level in sorted(levels):
            members = levels[level]
            units = self._family_units(project, members)

            def desired_center(unit: list[UUID]) -> float:
                parent_positions = [
                    positions[parent][0]
                    for person_id in unit
                    for parent in parent_order[person_id]
                    if parent in positions
                ]
                if parent_positions:
                    return sum(parent_positions) / len(parent_positions)
                return sum(people[person_id].layout.x for person_id in unit) / len(unit)

            units.sort(key=lambda unit: (desired_center(unit), str(unit[0])))
            total_width = (
                sum((len(unit) - 1) * self.HORIZONTAL_SPACING for unit in units)
                + max(0, len(units) - 1) * self.FAMILY_GAP
            )
            cursor = -total_width / 2
            provisional: dict[UUID, float] = {}
            unit_centers: list[float] = []
            for unit in units:
                unit_width = (len(unit) - 1) * self.HORIZONTAL_SPACING
                unit_centers.append(cursor + unit_width / 2)
                for index, person_id in enumerate(unit):
                    provisional[person_id] = cursor + index * self.HORIZONTAL_SPACING
                cursor += unit_width + self.FAMILY_GAP
            desired = [desired_center(unit) for unit in units if any(parent_order[p] for p in unit)]
            actual = [
                center
                for center, unit in zip(unit_centers, units, strict=True)
                if any(parent_order[p] for p in unit)
            ]
            shift = (sum(desired) / len(desired) - sum(actual) / len(actual)) if desired else 0.0
            for person_id in members:
                person = people[person_id]
                if preserve_locked and person.layout.locked:
                    positions[person_id] = (person.layout.x, person.layout.y)
                else:
                    positions[person_id] = (
                        provisional[person_id] + shift,
                        level * self.VERTICAL_SPACING,
                    )
        return positions

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
