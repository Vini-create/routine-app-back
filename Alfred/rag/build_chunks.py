from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from Alfred.rag.chunks import EMBEDDING_MODEL, Chunk, build_chunks
from Alfred.rag.loader import load_production_documents
from Alfred.rag.paths import BUILD_DIR


CHUNKS_PATH = BUILD_DIR / "chunks.jsonl"
MANIFEST_PATH = BUILD_DIR / "manifest.json"

CHUNK_SCHEMA_VERSION = "1.0.0"


def serialize_chunk(chunk: Chunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "content": chunk.content,
        "metadata": chunk.to_metadata(),
    }


def build_chunk_records() -> list[dict[str, Any]]:
    documents = load_production_documents()

    chunks = [
        chunk
        for document in documents
        for chunk in build_chunks(document)
    ]

    chunk_ids = [chunk.chunk_id for chunk in chunks]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Chunk IDs must be unique.")

    return [serialize_chunk(chunk) for chunk in chunks]


def write_build_artifacts() -> None:
    records = build_chunk_records()

    jsonl_content = "".join(
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for record in records
    )

    chunks_sha256 = hashlib.sha256(
        jsonl_content.encode("utf-8")
    ).hexdigest()

    manifest = {
        "chunk_schema_version": CHUNK_SCHEMA_VERSION,
        "embedding_model": EMBEDDING_MODEL,
        "chunking_strategy": "whole_document_when_within_token_limits",
        "production_documents": 45,
        "chunks": len(records),
        "chunks_sha256": chunks_sha256,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    CHUNKS_PATH.write_text(jsonl_content, encoding="utf-8")

    MANIFEST_PATH.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Built {len(records)} chunks.")
    print(f"Chunks: {CHUNKS_PATH}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Chunks SHA-256: {chunks_sha256}")


if __name__ == "__main__":
    write_build_artifacts()
