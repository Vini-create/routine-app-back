"""Strict loader for the versioned Alfred knowledge corpus.

Only the machine-audited build artifact is consumed at runtime. Archive,
quarantine and source-registry files never enter retrieval implicitly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CORPUS_BUILD_DIR = PROJECT_ROOT / "Alfred" / "rag" / "corpus" / "build"
CHUNKS_PATH = CORPUS_BUILD_DIR / "chunks.jsonl"
MANIFEST_PATH = CORPUS_BUILD_DIR / "manifest.json"

ALLOWED_DOCUMENT_TYPES = frozenset({"knowledge", "playbook"})
ALLOWED_STATUSES = frozenset({"machine_audited", "human_reviewed"})
MAX_CORPUS_CHUNKS = 10_000


@dataclass(frozen=True, slots=True)
class CorpusChunk:
    chunk_id: str
    document_id: str
    title: str
    content: str
    document_type: str
    topic_id: str
    language: str
    status: str
    source_path: str
    source_ids: tuple[str, ...]
    concept_id: str | None
    related_concept_ids: tuple[str, ...]

    def to_metadata(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "topic_id": self.topic_id,
            "language": self.language,
            "status": self.status,
            "source_path": self.source_path,
            "source_ids": list(self.source_ids),
            "concept_id": self.concept_id,
            "related_concept_ids": list(self.related_concept_ids),
        }


def _require_text(value: Any, *, field: str, chunk_id: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Chunk '{chunk_id}' has an invalid '{field}'.")
    return value.strip()


def _require_string_tuple(
    value: Any,
    *,
    field: str,
    chunk_id: str,
) -> tuple[str, ...]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"Chunk '{chunk_id}' has an invalid '{field}'.")
    return tuple(item.strip() for item in value)


def _title_from_markdown(content: str, *, chunk_id: str) -> str:
    first_line = content.splitlines()[0].strip()
    if not first_line.startswith("# "):
        raise ValueError(f"Chunk '{chunk_id}' must start with a Markdown title.")
    return _require_text(first_line[2:], field="title", chunk_id=chunk_id)


def _parse_chunk(record: Any, *, line_number: int) -> CorpusChunk:
    if not isinstance(record, dict):
        raise ValueError(f"Corpus line {line_number} must contain an object.")
    chunk_id = _require_text(
        record.get("chunk_id"),
        field="chunk_id",
        chunk_id=f"line-{line_number}",
    )
    content = _require_text(record.get("content"), field="content", chunk_id=chunk_id)
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"Chunk '{chunk_id}' has invalid metadata.")
    if metadata.get("chunk_id") != chunk_id:
        raise ValueError(f"Chunk '{chunk_id}' has mismatched metadata identity.")

    document_type = _require_text(
        metadata.get("document_type"),
        field="document_type",
        chunk_id=chunk_id,
    )
    status = _require_text(metadata.get("status"), field="status", chunk_id=chunk_id)
    language = _require_text(
        metadata.get("language"),
        field="language",
        chunk_id=chunk_id,
    )
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise ValueError(f"Chunk '{chunk_id}' has a forbidden document type.")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Chunk '{chunk_id}' is not approved for production.")
    if language != "en":
        raise ValueError(f"Chunk '{chunk_id}' is outside the canonical language.")

    concept_id = metadata.get("concept_id")
    if concept_id is not None and (
        not isinstance(concept_id, str) or not concept_id.strip()
    ):
        raise ValueError(f"Chunk '{chunk_id}' has an invalid concept_id.")

    return CorpusChunk(
        chunk_id=chunk_id,
        document_id=_require_text(
            metadata.get("document_id"),
            field="document_id",
            chunk_id=chunk_id,
        ),
        title=_title_from_markdown(content, chunk_id=chunk_id),
        content=content,
        document_type=document_type,
        topic_id=_require_text(
            metadata.get("topic_id"),
            field="topic_id",
            chunk_id=chunk_id,
        ),
        language=language,
        status=status,
        source_path=_require_text(
            metadata.get("source_path"),
            field="source_path",
            chunk_id=chunk_id,
        ),
        source_ids=_require_string_tuple(
            metadata.get("source_ids", []),
            field="source_ids",
            chunk_id=chunk_id,
        ),
        concept_id=concept_id.strip() if isinstance(concept_id, str) else None,
        related_concept_ids=_require_string_tuple(
            metadata.get("related_concept_ids", []),
            field="related_concept_ids",
            chunk_id=chunk_id,
        ),
    )


@lru_cache(maxsize=1)
def load_production_corpus(
    chunks_path: Path = CHUNKS_PATH,
    manifest_path: Path = MANIFEST_PATH,
) -> tuple[CorpusChunk, ...]:
    """Load and integrity-check only the canonical production artifact."""

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_bytes = chunks_path.read_bytes()
    expected_hash = manifest.get("chunks_sha256")
    actual_hash = hashlib.sha256(raw_bytes).hexdigest()
    if not isinstance(expected_hash, str) or actual_hash != expected_hash:
        raise ValueError("The RAG corpus hash does not match its build manifest.")

    records: list[CorpusChunk] = []
    for line_number, line in enumerate(raw_bytes.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON on corpus line {line_number}."
            ) from error
        records.append(_parse_chunk(parsed, line_number=line_number))

    expected_count = manifest.get("chunks")
    if not records or len(records) != expected_count:
        raise ValueError("The RAG corpus cardinality differs from its manifest.")
    if len(records) > MAX_CORPUS_CHUNKS:
        raise ValueError("The RAG corpus exceeds the runtime safety limit.")
    chunk_ids = [chunk.chunk_id for chunk in records]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("The RAG corpus contains duplicate chunk IDs.")
    return tuple(records)
