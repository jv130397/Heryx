from pathlib import Path

from rarepedigree.domain import GenderIdentity, Individual, PedigreeProject
from rarepedigree.persistence import JsonProjectRepository


def test_atomic_json_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "family.rps.json"
    project = PedigreeProject(
        title="Família sintética",
        individuals=[Individual(label="I-1", gender_identity=GenderIdentity.MAN)],
    )
    repository = JsonProjectRepository()
    repository.save(project, path)
    restored = repository.load(path)
    assert restored.project_id == project.project_id
    assert restored.individuals == project.individuals
    assert path.stat().st_mode & 0o077 == 0

