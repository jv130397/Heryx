"""Objective visual-quality measurements for a rendered pedigree."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QLineF, QPointF, QRectF

from rarepedigree.rendering.items import ParentageConnectorItem


@dataclass(frozen=True)
class LayoutQualityMetrics:
    symbol_collisions: int
    connector_symbol_intersections: int
    connector_crossings: int
    connector_overlaps: int
    total_connector_length: float
    maximum_connector_length: float


def measure_scene(scene) -> LayoutQualityMetrics:
    symbols = list(scene.person_items.values())
    symbol_collisions = sum(
        first.sceneBoundingRect().intersects(second.sceneBoundingRect())
        for index, first in enumerate(symbols)
        for second in symbols[index + 1 :]
    )
    connectors = list({id(item): item for item in scene.parentage_items.values()}.values())
    connector_symbol_intersections = 0
    lengths: list[float] = []
    for connector in connectors:
        endpoint_ids = {
            *(parent.person.id for parent in connector.parents),
            *(child.person.id for child in connector.children),
        }
        lengths.append(sum(segment.length() for segment in connector.segments))
        for segment in connector.segments:
            for symbol in symbols:
                if symbol.person.id in endpoint_ids:
                    continue
                bounds = symbol.sceneBoundingRect().adjusted(2, 2, -2, -2)
                if _line_intersects_rect(segment, bounds):
                    connector_symbol_intersections += 1
    crossings = 0
    overlaps = 0
    for index, first in enumerate(connectors):
        for second in connectors[index + 1 :]:
            if _share_endpoint(first, second):
                continue
            crossings += sum(
                _proper_intersection(first_segment, second_segment)
                for first_segment in first.segments
                for second_segment in second.segments
            )
            overlaps += sum(
                _collinear_overlap(first_segment, second_segment)
                for first_segment in first.segments
                for second_segment in second.segments
            )
    return LayoutQualityMetrics(
        symbol_collisions=symbol_collisions,
        connector_symbol_intersections=connector_symbol_intersections,
        connector_crossings=crossings,
        connector_overlaps=overlaps,
        total_connector_length=sum(lengths),
        maximum_connector_length=max(lengths, default=0.0),
    )


def audit_parentage_connectors(scene) -> list[dict[str, object]]:
    """Describe every rendered nucleus and its geometric conflicts."""
    connectors = list({id(item): item for item in scene.parentage_items.values()}.values())
    result = []
    for connector in connectors:
        conflicts = []
        for other in connectors:
            if other is connector or _share_endpoint(connector, other):
                continue
            crossing_count = sum(
                _proper_intersection(first, second)
                for first in connector.segments
                for second in other.segments
            )
            overlap_count = sum(
                _collinear_overlap(first, second)
                for first in connector.segments
                for second in other.segments
            )
            if crossing_count or overlap_count:
                conflicts.append(
                    {
                        "parents": [item.person.label for item in other.parents],
                        "children": [item.person.label for item in other.children],
                        "crossings": crossing_count,
                        "overlaps": overlap_count,
                    }
                )
        result.append(
            {
                "parents": [item.person.label for item in connector.parents],
                "parent_x": [item.pos().x() for item in connector.parents],
                "children": [item.person.label for item in connector.children],
                "child_x": [item.pos().x() for item in connector.children],
                "kinds": sorted({edge.kind.value for edge in connector.edges}),
                "evidence": sorted({edge.evidence_status.value for edge in connector.edges}),
                "routing_offset": connector.routing_offset,
                "conflicts": conflicts,
            }
        )
    return result


def _share_endpoint(first: ParentageConnectorItem, second: ParentageConnectorItem) -> bool:
    first_ids = {item.person.id for item in (*first.parents, *first.children)}
    second_ids = {item.person.id for item in (*second.parents, *second.children)}
    return bool(first_ids & second_ids)


def _proper_intersection(first: QLineF, second: QLineF) -> bool:
    intersection_type, point = first.intersects(second)
    if intersection_type != QLineF.IntersectionType.BoundedIntersection:
        return False
    return not any(
        _near(point, endpoint)
        for endpoint in (first.p1(), first.p2(), second.p1(), second.p2())
    )


def _collinear_overlap(first: QLineF, second: QLineF, tolerance: float = 0.5) -> bool:
    first_horizontal = abs(first.dy()) <= tolerance
    second_horizontal = abs(second.dy()) <= tolerance
    first_vertical = abs(first.dx()) <= tolerance
    second_vertical = abs(second.dx()) <= tolerance
    if first_horizontal and second_horizontal and abs(first.y1() - second.y1()) <= tolerance:
        return _range_overlap(first.x1(), first.x2(), second.x1(), second.x2()) > tolerance
    if first_vertical and second_vertical and abs(first.x1() - second.x1()) <= tolerance:
        return _range_overlap(first.y1(), first.y2(), second.y1(), second.y2()) > tolerance
    return False


def _range_overlap(first_a: float, first_b: float, second_a: float, second_b: float) -> float:
    first_low, first_high = sorted((first_a, first_b))
    second_low, second_high = sorted((second_a, second_b))
    return max(0.0, min(first_high, second_high) - max(first_low, second_low))


def _near(first: QPointF, second: QPointF, tolerance: float = 0.5) -> bool:
    return abs(first.x() - second.x()) <= tolerance and abs(first.y() - second.y()) <= tolerance


def _line_intersects_rect(line: QLineF, rect: QRectF) -> bool:
    if rect.contains(line.p1()) or rect.contains(line.p2()):
        return True
    corners = (rect.topLeft(), rect.topRight(), rect.bottomRight(), rect.bottomLeft())
    edges = [QLineF(corners[index], corners[(index + 1) % 4]) for index in range(4)]
    return any(
        line.intersects(edge)[0] == QLineF.IntersectionType.BoundedIntersection
        for edge in edges
    )
