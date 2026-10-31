from pathlib import Path

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    LayoutPosition,
    Parentage,
    PedigreeProject,
    Relationship,
    RelationshipKind,
)
from rarepedigree.rendering import PedigreeScene
from rarepedigree.rendering.exporters import export_pdf, export_png, export_svg


def test_scene_and_exporters_render_basic_symbols(qapp, tmp_path: Path) -> None:
    del qapp
    project = PedigreeProject(
        individuals=[
            Individual(
                label="I-1",
                gender_identity=GenderIdentity.WOMAN,
                layout=LayoutPosition(x=10, y=20),
            )
        ]
    )
    scene = PedigreeScene()
    scene.load_project(project)
    svg_path = tmp_path / "pedigree.svg"
    png_path = tmp_path / "pedigree.png"
    pdf_path = tmp_path / "pedigree.pdf"
    export_svg(scene, svg_path)
    export_png(scene, png_path)
    export_pdf(scene, pdf_path)
    assert b"<svg" in svg_path.read_bytes()
    assert png_path.read_bytes().startswith(b"\x89PNG")
    assert pdf_path.read_bytes().startswith(b"%PDF")


def test_parentage_connectors_and_generation_labels(qapp) -> None:
    del qapp
    child = Individual()
    project = PedigreeProject(individuals=[child])
    project, _ = FamilyService.add_parents(project, child.id)
    scene = PedigreeScene()
    scene.load_project(project)
    assert child.id in scene.parentage_items
    assert len(scene.generation_items) == 2
    assert len({label.pos().x() for label in scene.generation_items}) == 1


def test_independent_grandparent_nuclei_use_distinct_connectors(qapp) -> None:
    del qapp
    grandparents = [
        Individual(label=f"G{index}", layout=LayoutPosition(x=index * 130, y=0))
        for index in range(4)
    ]
    parents = [
        Individual(label="P1", layout=LayoutPosition(x=65, y=180)),
        Individual(label="P2", layout=LayoutPosition(x=325, y=180)),
    ]
    project = PedigreeProject(
        individuals=[*grandparents, *parents],
        parentages=[
            Parentage(parent_id=grandparents[0].id, child_id=parents[0].id),
            Parentage(parent_id=grandparents[1].id, child_id=parents[0].id),
            Parentage(parent_id=grandparents[2].id, child_id=parents[1].id),
            Parentage(parent_id=grandparents[3].id, child_id=parents[1].id),
        ],
    )
    scene = PedigreeScene()
    scene.load_project(project)
    first_item = scene.parentage_items[parents[0].id]
    second_item = scene.parentage_items[parents[1].id]
    assert first_item is not second_item
    assert not first_item.path().boundingRect().intersects(second_item.path().boundingRect())


def test_full_siblings_share_one_scientific_sibship_connector(qapp) -> None:
    del qapp
    first = Individual(layout=LayoutPosition(x=-65, y=180))
    second = Individual(layout=LayoutPosition(x=65, y=180))
    parents = [
        Individual(layout=LayoutPosition(x=-65, y=0)),
        Individual(layout=LayoutPosition(x=65, y=0)),
    ]
    project = PedigreeProject(
        individuals=[*parents, first, second],
        parentages=[
            Parentage(parent_id=parent.id, child_id=child.id)
            for parent in parents
            for child in (first, second)
        ],
    )
    scene = PedigreeScene()
    scene.load_project(project)
    assert scene.parentage_items[first.id] is scene.parentage_items[second.id]


def test_reproductive_lanes_follow_visual_order_not_uuid_order(qapp) -> None:
    del qapp
    parents = [
        Individual(label=f"P{index}", layout=LayoutPosition(x=index * 260, y=0))
        for index in range(3)
    ]
    children = [
        Individual(label=f"C{index}", layout=LayoutPosition(x=index * 260, y=180))
        for index in range(3)
    ]
    project = PedigreeProject(
        individuals=[*reversed(parents), *children],
        parentages=[
            Parentage(parent_id=parent.id, child_id=child.id)
            for parent, child in zip(parents, children, strict=True)
        ],
    )
    scene = PedigreeScene()
    scene.load_project(project)
    offsets = [scene.parentage_items[child.id].routing_offset for child in children]
    assert offsets == [0.0, 14.0, -14.0]


def test_long_identifier_participates_in_scene_bounds(qapp) -> None:
    del qapp
    person = Individual(label="Primo materno identificado")
    scene = PedigreeScene()
    scene.load_project(PedigreeProject(individuals=[person]))
    assert scene.person_items[person.id].boundingRect().width() > 150


def test_consanguineous_partnership_reaches_the_graphics_scene(qapp) -> None:
    del qapp
    first = Individual(layout=LayoutPosition(x=-80, y=0))
    second = Individual(layout=LayoutPosition(x=80, y=0))
    relationship = Relationship(
        member_a=first.id,
        member_b=second.id,
        kind=RelationshipKind.CONSANGUINEOUS_PARTNERSHIP,
    )
    project = PedigreeProject(individuals=[first, second], relationships=[relationship])
    scene = PedigreeScene()
    scene.load_project(project)
    rendered = scene.relationship_items[relationship.id]
    assert rendered.relationship.kind == RelationshipKind.CONSANGUINEOUS_PARTNERSHIP
    assert rendered.boundingRect().width() > 0
