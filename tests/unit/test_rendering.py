from pathlib import Path

from rarepedigree.domain import GenderIdentity, Individual, LayoutPosition, PedigreeProject
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
