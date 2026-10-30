from pathlib import Path

from rarepedigree.domain import (
    FamilyService,
    GenderIdentity,
    Individual,
    LayoutPosition,
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
