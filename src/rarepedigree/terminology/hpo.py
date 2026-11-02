"""Official HPO OBO ingestion and local, offline SQLite search."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import sqlite3
import tempfile
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from platformdirs import user_data_path

HPO_OBO_URL = "https://purl.obolibrary.org/obo/hp.obo"
HPO_PROJECT_URL = "https://hpo.jax.org/"
HPO_ACKNOWLEDGEMENT = "This product uses the Human Phenotype Ontology (HPO)."


@dataclass(slots=True)
class HPOTerm:
    id: str
    name: str
    definition: str = ""
    synonyms: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)
    alternative_ids: list[str] = field(default_factory=list)
    obsolete: bool = False
    replaced_by: str | None = None


@dataclass(frozen=True, slots=True)
class HPORelease:
    version: str
    date: str | None
    source: str
    installed_at: str
    sha256: str
    term_count: int


def _unquote(value: str) -> str:
    match = re.match(r'^"((?:[^"\\]|\\.)*)"', value)
    return bytes(match.group(1), "utf-8").decode("unicode_escape") if match else value


def parse_obo(path: Path) -> tuple[dict[str, str], list[HPOTerm]]:
    """Parse the HPO subset needed by the application without changing ontology content."""
    header: dict[str, str] = {}
    terms: list[HPOTerm] = []
    current: dict[str, list[str]] | None = None
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if line == "[Term]":
                if current:
                    term = _term_from_fields(current)
                    if term:
                        terms.append(term)
                current = {}
                continue
            if line.startswith("["):
                if current:
                    term = _term_from_fields(current)
                    if term:
                        terms.append(term)
                current = None
                continue
            if not line or line.startswith("!") or ": " not in line:
                continue
            key, value = line.split(": ", 1)
            if current is None:
                header.setdefault(key, value)
            else:
                current.setdefault(key, []).append(value)
    if current:
        term = _term_from_fields(current)
        if term:
            terms.append(term)
    return header, terms


def _term_from_fields(fields: dict[str, list[str]]) -> HPOTerm | None:
    if "id" not in fields or "name" not in fields or not fields["id"][0].startswith("HP:"):
        return None
    return HPOTerm(
        id=fields["id"][0],
        name=fields["name"][0],
        definition=_unquote(fields.get("def", [""])[0]),
        synonyms=[_unquote(value) for value in fields.get("synonym", [])],
        parents=[value.split()[0] for value in fields.get("is_a", [])],
        alternative_ids=fields.get("alt_id", []),
        obsolete=fields.get("is_obsolete", ["false"])[0].lower() == "true",
        replaced_by=fields.get("replaced_by", [None])[0],
    )


class HPOIndex:
    """Read-only query facade over an installed HPO SQLite database."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_hpo_database_path()

    @property
    def installed(self) -> bool:
        return self.path.is_file()

    def metadata(self) -> HPORelease | None:
        if not self.installed:
            return None
        with sqlite3.connect(self.path) as connection:
            data = dict(connection.execute("SELECT key, value FROM metadata"))
            return HPORelease(
                version=data["version"],
                date=data.get("date"),
                source=data["source"],
                installed_at=data["installed_at"],
                sha256=data["sha256"],
                term_count=int(data["term_count"]),
            )

    def term(self, hpo_id: str) -> HPOTerm | None:
        if not self.installed:
            return None
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT t.* FROM terms t LEFT JOIN alternative_ids a ON a.term_id=t.id "
                "WHERE t.id=? OR a.alt_id=? LIMIT 1",
                (hpo_id.upper(), hpo_id.upper()),
            ).fetchone()
            return self._hydrate(connection, row) if row else None

    def search(self, query: str, limit: int = 20) -> list[HPOTerm]:
        query = query.strip()
        if not query or not self.installed:
            return []
        limit = max(1, min(limit, 100))
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            exact = connection.execute(
                "SELECT t.* FROM terms t LEFT JOIN alternative_ids a ON a.term_id=t.id "
                "WHERE upper(t.id)=upper(?) OR upper(a.alt_id)=upper(?) LIMIT ?",
                (query, query, limit),
            ).fetchall()
            rows = list(exact)
            if len(rows) < limit:
                tokens = [re.sub(r"[^\w]", "", token) for token in query.split()]
                fts_query = " AND ".join(f'"{token}"*' for token in tokens if token)
                if fts_query:
                    matched = connection.execute(
                        "SELECT t.* FROM term_search s JOIN terms t ON t.id=s.term_id "
                        "WHERE term_search MATCH ? ORDER BY bm25(term_search) LIMIT ?",
                        (fts_query, limit),
                    ).fetchall()
                    known = {row["id"] for row in rows}
                    rows.extend(row for row in matched if row["id"] not in known)
            return [self._hydrate(connection, row) for row in rows[:limit]]

    def children(self, hpo_id: str) -> list[HPOTerm]:
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT t.* FROM parents p JOIN terms t ON t.id=p.term_id "
                "WHERE p.parent_id=? ORDER BY t.name",
                (hpo_id,),
            ).fetchall()
            return [self._hydrate(connection, row) for row in rows]

    @staticmethod
    def _hydrate(connection: sqlite3.Connection, row: sqlite3.Row) -> HPOTerm:
        term_id = row["id"]
        synonyms = [
            value[0]
            for value in connection.execute(
                "SELECT synonym FROM synonyms WHERE term_id=? ORDER BY synonym", (term_id,)
            )
        ]
        parents = [
            value[0]
            for value in connection.execute(
                "SELECT parent_id FROM parents WHERE term_id=?", (term_id,)
            )
        ]
        alternative_ids = [
            value[0]
            for value in connection.execute(
                "SELECT alt_id FROM alternative_ids WHERE term_id=?", (term_id,)
            )
        ]
        return HPOTerm(
            id=term_id,
            name=row["name"],
            definition=row["definition"],
            synonyms=synonyms,
            parents=parents,
            alternative_ids=alternative_ids,
            obsolete=bool(row["obsolete"]),
            replaced_by=row["replaced_by"],
        )


def default_hpo_database_path() -> Path:
    return user_data_path("RarePedigreeStudio", "RarePedigree") / "terminology" / "hpo.sqlite3"


def build_hpo_database(
    obo_path: Path,
    database_path: Path,
    *,
    source: str = HPO_OBO_URL,
    minimum_terms: int = 1,
) -> HPORelease:
    header, terms = parse_obo(obo_path)
    if len(terms) < minimum_terms:
        raise ValueError(f"HPO integrity check failed: only {len(terms)} terms")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".hpo-index-", suffix=".sqlite3", dir=database_path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    sha256 = hashlib.sha256(obo_path.read_bytes()).hexdigest()
    version = header.get("data-version", header.get("date", "unknown"))
    release = HPORelease(
        version=version,
        date=header.get("date"),
        source=source,
        installed_at=datetime.now(UTC).isoformat(),
        sha256=sha256,
        term_count=len(terms),
    )
    try:
        with sqlite3.connect(temporary) as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=DELETE;
                CREATE TABLE terms(id TEXT PRIMARY KEY, name TEXT NOT NULL,
                  definition TEXT NOT NULL, obsolete INTEGER NOT NULL, replaced_by TEXT);
                CREATE TABLE synonyms(term_id TEXT NOT NULL, synonym TEXT NOT NULL);
                CREATE INDEX synonyms_term ON synonyms(term_id);
                CREATE TABLE parents(term_id TEXT NOT NULL, parent_id TEXT NOT NULL);
                CREATE INDEX parents_parent ON parents(parent_id);
                CREATE TABLE alternative_ids(alt_id TEXT PRIMARY KEY, term_id TEXT NOT NULL);
                CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE VIRTUAL TABLE term_search USING fts5(term_id UNINDEXED, name, synonyms,
                  tokenize='unicode61 remove_diacritics 2');
                """
            )
            for term in terms:
                connection.execute(
                    "INSERT INTO terms VALUES(?,?,?,?,?)",
                    (term.id, term.name, term.definition, term.obsolete, term.replaced_by),
                )
                connection.executemany(
                    "INSERT INTO synonyms VALUES(?,?)",
                    ((term.id, synonym) for synonym in term.synonyms),
                )
                connection.executemany(
                    "INSERT INTO parents VALUES(?,?)",
                    ((term.id, parent) for parent in term.parents),
                )
                connection.executemany(
                    "INSERT OR IGNORE INTO alternative_ids VALUES(?,?)",
                    ((alternative_id, term.id) for alternative_id in term.alternative_ids),
                )
                connection.execute(
                    "INSERT INTO term_search VALUES(?,?,?)",
                    (term.id, term.name, " ".join(term.synonyms)),
                )
            connection.executemany(
                "INSERT INTO metadata VALUES(?,?)",
                ((key, str(value)) for key, value in asdict(release).items() if value is not None),
            )
            connection.execute("PRAGMA quick_check").fetchone()
        os.replace(temporary, database_path)
    finally:
        temporary.unlink(missing_ok=True)
    return release


def install_official_hpo(
    database_path: Path | None = None,
    *,
    url: str = HPO_OBO_URL,
    timeout: int = 60,
) -> HPORelease:
    """Download only official ontology data and atomically replace a validated index."""
    target = database_path or default_hpo_database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rarepedigree-hpo-") as directory:
        obo_path = Path(directory) / "hp.obo"
        request = urllib.request.Request(url, headers={"User-Agent": "RarePedigreeStudio/0.2"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            with obo_path.open("wb") as output:
                _copy_limited(response, output, 64 * 1024 * 1024)
        return build_hpo_database(obo_path, target, source=url, minimum_terms=10_000)


def _copy_limited(source: BinaryIO, destination: BinaryIO, maximum: int) -> None:
    copied = 0
    while chunk := source.read(1024 * 1024):
        copied += len(chunk)
        if copied > maximum:
            raise ValueError("HPO download exceeds safety limit")
        destination.write(chunk)


def backup_hpo_database(path: Path | None = None) -> Path | None:
    source = path or default_hpo_database_path()
    if not source.exists():
        return None
    backup = source.with_suffix(".previous.sqlite3")
    shutil.copy2(source, backup)
    return backup
