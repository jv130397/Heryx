from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOMAIN = PROJECT_ROOT / "src" / "rarepedigree" / "domain"
FORBIDDEN_ROOTS = {"PySide6", "sqlite3", "rarepedigree.persistence", "rarepedigree.ui"}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_domain_does_not_depend_on_gui_or_persistence() -> None:
    violations: list[str] = []
    for path in DOMAIN.rglob("*.py"):
        for imported in _imports(path):
            if any(imported == root or imported.startswith(f"{root}.") for root in FORBIDDEN_ROOTS):
                violations.append(f"{path.relative_to(PROJECT_ROOT)} imports {imported}")
    assert not violations, "\n".join(violations)
