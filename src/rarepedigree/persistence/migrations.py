"""Versioned, lossless migrations for native project dictionaries."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import NAMESPACE_URL, uuid5

CURRENT_SCHEMA_VERSION = "0.2.0"


def migrate_project(data: dict[str, Any]) -> dict[str, Any]:
    migrated = deepcopy(data)
    version = migrated.get("schema_version", "0.1.0")
    if version == "0.1.0":
        project_id = str(migrated["project_id"])
        migrated["family"] = {
            "id": str(uuid5(NAMESPACE_URL, f"rarepedigree-family:{project_id}")),
            "label": migrated.get("title", "Família"),
        }
        migrated.setdefault("parentages", [])
        migrated.setdefault("twin_groups", [])
        for person in migrated.get("individuals", []):
            person.setdefault("placeholder", False)
            person.setdefault("layout", {}).setdefault("locked", False)
        migrated["schema_version"] = "0.2.0"
        version = "0.2.0"
    if version != CURRENT_SCHEMA_VERSION:
        raise ValueError(f"unsupported project schema version: {version}")
    return migrated
