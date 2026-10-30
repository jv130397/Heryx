"""Defensive, atomic persistence for the native JSON project format."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from rarepedigree.domain import PedigreeProject

MAX_PROJECT_BYTES = 20 * 1024 * 1024


class JsonProjectRepository:
    """Load and save native projects without executing imported content."""

    def load(self, path: Path) -> PedigreeProject:
        if path.stat().st_size > MAX_PROJECT_BYTES:
            raise ValueError("project exceeds the 20 MiB safety limit")
        return PedigreeProject.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, project: PedigreeProject, path: Path) -> None:
        path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        project.touch()
        payload = project.model_dump_json(indent=2)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            temporary_path.chmod(0o600)
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)

