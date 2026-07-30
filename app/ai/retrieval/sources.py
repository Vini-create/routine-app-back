"""Validated public citations resolved from Alfred's source registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SOURCE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "Alfred"
    / "rag"
    / "corpus"
    / "source_registry.jsonl"
)
ALLOWED_VERIFICATION_STATUSES = frozenset(
    {
        "verified_primary",
        "verified_official_repository",
        "verified_reliable_secondary",
    }
)


def _required_text(record: dict[str, Any], field: str, source_id: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Source '{source_id}' has an invalid '{field}'.")
    return value.strip()


@dataclass(frozen=True, slots=True)
class PublicSource:
    source_id: str
    title: str
    authors: tuple[str, ...]
    publication_year: int | None
    url: str
    doi: str | None

    def public(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "authors": list(self.authors),
            "publication_year": self.publication_year,
            "url": self.url,
            "doi": self.doi,
        }


def _parse_source(record: Any, line_number: int) -> PublicSource | None:
    if not isinstance(record, dict):
        raise ValueError(f"Source registry line {line_number} is not an object.")
    source_id = _required_text(record, "source_id", f"line-{line_number}")
    if (
        record.get("active") is not True
        or record.get("verification_status") not in ALLOWED_VERIFICATION_STATUSES
    ):
        return None

    raw_authors = record.get("authors")
    if not isinstance(raw_authors, list) or any(
        not isinstance(author, str) or not author.strip() for author in raw_authors
    ):
        raise ValueError(f"Source '{source_id}' has invalid authors.")
    raw_year = record.get("publication_year")
    if raw_year is not None and not isinstance(raw_year, int):
        raise ValueError(f"Source '{source_id}' has an invalid publication year.")
    url = _required_text(record, "url", source_id)
    parsed_url = urlsplit(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError(f"Source '{source_id}' has an invalid public URL.")
    raw_doi = record.get("doi")
    doi = raw_doi.strip() if isinstance(raw_doi, str) and raw_doi.strip() else None
    return PublicSource(
        source_id=source_id,
        title=_required_text(record, "title", source_id),
        authors=tuple(author.strip() for author in raw_authors),
        publication_year=raw_year,
        url=url,
        doi=doi,
    )


@lru_cache(maxsize=1)
def load_public_source_registry() -> dict[str, PublicSource]:
    sources: dict[str, PublicSource] = {}
    for line_number, line in enumerate(
        SOURCE_REGISTRY_PATH.read_text(encoding="utf-8").splitlines(),
        1,
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON on source registry line {line_number}."
            ) from error
        source = _parse_source(record, line_number)
        if source is None:
            continue
        if source.source_id in sources:
            raise ValueError(f"Duplicate source ID '{source.source_id}'.")
        sources[source.source_id] = source
    if not sources:
        raise ValueError("The public source registry is empty.")
    return sources


def resolve_public_sources(
    source_ids: list[str],
    *,
    limit: int = 12,
) -> list[dict[str, Any]]:
    registry = load_public_source_registry()
    resolved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_id in source_ids:
        if source_id in seen:
            continue
        seen.add(source_id)
        source = registry.get(source_id)
        if source is not None:
            resolved.append(source.public())
        if len(resolved) >= limit:
            break
    return resolved
