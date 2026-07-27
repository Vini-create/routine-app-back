from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from Alfred.rag.paths import CORPUS_DIR


DOCUMENT_REGISTRY_PATH = CORPUS_DIR / "document_registry.jsonl"

@dataclass
class LoadedDocument:
    document_id: str
    path: Path
    registry: dict[str, Any]
    metadata: dict[str, Any]
    body: str

def read_document_registry() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with DOCUMENT_REGISTRY_PATH.open("r", encoding="utf-8") as file:
        for line_number ,line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Error by decoding JSON in line {line_number}: {error}, in document {DOCUMENT_REGISTRY_PATH}") from error
            rows.append(row)
        return rows
    
def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"File {path} does not contain YAML front matter.")
    parts = text.split("---", maxsplit=2)
    if len(parts) != 3:
        raise ValueError(f"File {path} does not contain valid YAML front matter.")
    yaml_text = parts[1]
    body = parts[2].strip()
    try:
        metadata = yaml.safe_load(yaml_text)
    except yaml.YAMLError as error:
        raise ValueError(f"Error parsing YAML front matter in file {path}: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError(f"YAML front matter in file {path} is not a dictionary.")
    if not body:
        raise ValueError(f"File {path} does not contain a body after the YAML front matter.")
    return metadata, body

def load_production_documents() -> list[LoadedDocument]:
    document_registry = read_document_registry()
    loaded_documents: list[LoadedDocument] = []
    for row in document_registry:
        if not row.get ("index_in_production", False):
            continue
        path = CORPUS_DIR / row["path"]
        if not path.is_file():
            raise FileNotFoundError(f"Document file {path} listed on registry does not exist.")
        metadata, body = read_markdown(path)
        if metadata.get("id") != row["document_id"]:
            raise ValueError(f"Document ID mismatch for file {path}: registry has {row['document_id']}, but YAML front matter has {metadata.get('id')}.")
        if metadata.get("topic_id") != row["topic_id"]:
            raise ValueError(f"Topic ID mismatch for file {path}: registry has {row['topic_id']}, but YAML front matter has {metadata.get('topic_id')}.")
        loaded_documents.append(
            LoadedDocument(
                document_id=row["document_id"],
                path=path,
                registry=row,
                metadata=metadata,
                body=body
            )
        )
    return loaded_documents

if __name__ == "__main__":
    documents = load_production_documents()
    print(f"Loaded {len(documents)} production documents:")
    for doc in documents:
        print(f"- {doc.document_id} ({doc.path} {doc.metadata['document_type']} {doc.metadata['topic_id']})")
    first_doc = documents[0]
    print("\n---First document example:---\n")
    print("Metadata:")
    print(first_doc.metadata)
    print("\nBody:")   
    print(first_doc.body[:300])
