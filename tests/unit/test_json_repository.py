from pathlib import Path

from rarepedigree.domain import FamilyService, GenderIdentity, Individual, PedigreeProject
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


def test_multigenerational_project_reopens_intact(tmp_path: Path) -> None:
    root = Individual(label="II-1")
    project = PedigreeProject(individuals=[root])
    project, parents = FamilyService.add_parents(project, root.id)
    project, _ = FamilyService.add_parents(project, parents[0])
    path = tmp_path / "three-generations.rps.json"
    repository = JsonProjectRepository()
    repository.save(project, path)
    restored = repository.load(path)
    assert restored == project
    assert len(restored.individuals) == 5
    assert len(restored.parentages) == 4
