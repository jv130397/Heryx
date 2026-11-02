import json
from pathlib import Path

from rarepedigree.persistence import JsonProjectRepository

FIXTURE = Path(__file__).parents[1] / "fixtures" / "schema_0_1_0.rps.json"


def test_schema_0_1_0_migrates_without_changing_uuids() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    project = JsonProjectRepository().load(FIXTURE)
    assert project.schema_version == "0.4.0"
    assert project.annotations == []
    assert project.hpo_observations == []
    assert str(project.project_id) == raw["project_id"]
    assert [str(person.id) for person in project.individuals] == [
        person["id"] for person in raw["individuals"]
    ]
    assert [str(item.id) for item in project.relationships] == [
        item["id"] for item in raw["relationships"]
    ]
    assert project.parentages == []
