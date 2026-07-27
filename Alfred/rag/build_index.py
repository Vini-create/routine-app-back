from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from dotenv import load_dotenv

from Alfred.rag.build_chunks import CHUNKS_PATH, MANIFEST_PATH
from Alfred.rag.embeddings import OpenAIEmbedder
from Alfred.rag.paths import INDEX_DIR, PROJECT_ROOT


INDEX_MANIFEST_PATH = INDEX_DIR / "manifest.json"

INDEX_FILENAMES = {
    "knowledge": "knowledge",
    "playbook": "playbooks",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}."
                ) from error

            if not isinstance(record, dict):
                raise ValueError(
                    f"Line {line_number} of {path} must contain a JSON object."
                )

            records.append(record)

    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    content = "".join(
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for record in records
    )

    path.write_text(content, encoding="utf-8")


def validate_chunk_record(record: dict[str, Any]) -> None:
    chunk_id = record.get("chunk_id")
    content = record.get("content")
    metadata = record.get("metadata")

    if not isinstance(chunk_id, str) or not chunk_id:
        raise ValueError("Every chunk record must have a non-empty chunk_id.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"Chunk '{chunk_id}' must have non-empty content.")

    if not isinstance(metadata, dict):
        raise ValueError(f"Chunk '{chunk_id}' must have metadata.")

    if metadata.get("document_type") not in INDEX_FILENAMES:
        raise ValueError(
            f"Chunk '{chunk_id}' has an unsupported document type."
        )


def build_faiss_index(
    index_name: str,
    records: list[dict[str, Any]],
    embedder: OpenAIEmbedder,
) -> dict[str, Any]:
    texts = [record["content"] for record in records]
    vectors = embedder.embed_documents(texts)

    vector_matrix = np.asarray(vectors, dtype=np.float32)

    if vector_matrix.ndim != 2 or vector_matrix.shape[0] != len(records):
        raise RuntimeError(
            f"Invalid embedding matrix for the '{index_name}' index."
        )

    faiss.normalize_L2(vector_matrix)

    dimension = vector_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(vector_matrix)

    index_path = INDEX_DIR / f"{index_name}.faiss"
    metadata_path = INDEX_DIR / f"{index_name}.metadata.jsonl"

    faiss.write_index(index, str(index_path))
    write_jsonl(metadata_path, records)

    return {
        "chunks": len(records),
        "dimension": dimension,
        "index_file": index_path.name,
        "metadata_file": metadata_path.name,
        "metric": "cosine_similarity",
    }


def build_indexes() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    if not CHUNKS_PATH.is_file() or not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            "Build chunks before building FAISS indexes."
        )

    chunks_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = read_jsonl(CHUNKS_PATH)

    if not records:
        raise ValueError("The chunks build artifact is empty.")

    for record in records:
        validate_chunk_record(record)

    chunk_ids = [record["chunk_id"] for record in records]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Chunk IDs must be unique before indexing.")

    grouped_records = {
        document_type: [
            record
            for record in records
            if record["metadata"]["document_type"] == document_type
        ]
        for document_type in INDEX_FILENAMES
    }

    if any(not group for group in grouped_records.values()):
        raise ValueError("Every FAISS index must contain at least one chunk.")

    embedder = OpenAIEmbedder()

    if chunks_manifest["embedding_model"] != embedder.config.model:
        raise ValueError(
            "The chunks artifact was built for a different embedding model."
        )

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    indexes = {
        INDEX_FILENAMES[document_type]: build_faiss_index(
            index_name=INDEX_FILENAMES[document_type],
            records=group,
            embedder=embedder,
        )
        for document_type, group in grouped_records.items()
    }

    index_manifest = {
        "chunks_sha256": chunks_manifest["chunks_sha256"],
        "embedding_model": embedder.config.model,
        "generated_at": datetime.now(UTC).isoformat(),
        "indexes": indexes,
    }

    INDEX_MANIFEST_PATH.write_text(
        json.dumps(
            index_manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Built {len(records)} FAISS records.")
    print(f"Indexes: {INDEX_DIR}")
    print(f"Embedding model: {embedder.config.model}")


if __name__ == "__main__":
    build_indexes()
