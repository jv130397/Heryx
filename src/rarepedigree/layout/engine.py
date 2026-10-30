"""Qt-independent multigenerational pedigree layout."""

from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from rarepedigree.domain import PedigreeProject


class PedigreeLayoutEngine:
    HORIZONTAL_SPACING = 130.0
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
            members.sort(
                key=lambda person_id: (
                    sum(people[parent].layout.x for parent in parent_order[person_id])
                    / max(1, len(parent_order[person_id])),
                    people[person_id].layout.x,
                    str(person_id),
                )
            )
            start = -(len(members) - 1) * self.HORIZONTAL_SPACING / 2
            for index, person_id in enumerate(members):
                person = people[person_id]
                if preserve_locked and person.layout.locked:
                    positions[person_id] = (person.layout.x, person.layout.y)
                else:
                    positions[person_id] = (
                        start + index * self.HORIZONTAL_SPACING,
                        level * self.VERTICAL_SPACING,
                    )
        return positions
