#!/usr/bin/env python3
"""Validate the Alfred-only canonical RAG and its migration boundaries."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

import yaml


RAG = Path(__file__).resolve().parents[1]
CANONICAL = RAG / "canonical"
ERRORS: list[str] = []
WARNINGS: list[str] = []
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOC_ID = re.compile(r"^(?:kd|pb)-[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_ID = re.compile(r"^src-[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_DOCUMENT_STATUSES = {
    "draft", "machine_audited", "human_reviewed", "deprecated", "archived", "quarantined",
}
INDEXABLE_STATUSES = {"machine_audited", "human_reviewed"}
ALLOWED_QUOTE_STATUSES = {
    "verified_primary_source", "verified_official_edition", "verified_reliable_secondary",
}
ACTIVE_SOURCE_STATUSES = {
    "verified_primary", "verified_official_repository", "verified_reliable_secondary",
}
KNOWLEDGE_HEADINGS = (
    "## Operational definition",
    "## What this concept does not mean",
    "## Main mechanisms",
    "## Evidence summary",
    "## Evidence mapping",
    "## Relevant signals",
    "## Alternative explanations",
    "## Information needed",
    "## Practical implications",
    "## Limitations",
    "## Sources",
)
PLAYBOOK_HEADINGS = (
    "## Activation criteria",
    "## Similar situations that should not activate this playbook",
    "## Possible explanations",
    "## Missing information",
    "## Response objective",
    "## Decision path",
    "## Candidate strategies",
    "## Conditions for selecting each strategy",
    "## When to ask a question",
    "## When to respond directly",
    "## What to avoid",
    "## Suggested next step",
    "## Related knowledge",
)


def error(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def relative(path: Path) -> str:
    return path.relative_to(RAG).as_posix()


def resolve_migration_path(value: object) -> Path:
    """Resolve paths recorded before the corpus moved under Alfred/rag."""
    path = Path(str(value or ""))

    # FILE_MAPPING e um registro historico: seus valores continuam com o
    # prefixo ``rag/`` original. Hoje esse prefixo representa a raiz de
    # ``Alfred/rag/corpus``, sem exigir a reescrita do inventario de migracao.
    if path.parts and path.parts[0] == "rag":
        return RAG.joinpath(*path.parts[1:])

    return RAG / path


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            error(f"{relative(path)}:{number}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            error(f"{relative(path)}:{number}: JSONL row is not an object")
        else:
            rows.append(value)
    return rows


def load_frontmatter(path: Path) -> tuple[dict, str] | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        error(f"{relative(path)}: missing YAML frontmatter")
        return None
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        error(f"{relative(path)}: invalid YAML: {exc}")
        return None
    if not isinstance(metadata, dict):
        error(f"{relative(path)}: frontmatter is not an object")
        return None
    return metadata, text[match.end():]


def require_fields(label: str, row: dict, fields: tuple[str, ...]) -> None:
    for field in fields:
        if field not in row:
            error(f"{label}: missing field {field}")


def validate_status(label: str, row: dict) -> None:
    status = row.get("status")
    if status not in ALLOWED_DOCUMENT_STATUSES:
        error(f"{label}: invalid document status {status!r}")
    if not isinstance(row.get("requires_human_review"), bool):
        error(f"{label}: requires_human_review must be boolean")
    if status != "human_reviewed" and row.get("requires_human_review") is not True:
        error(f"{label}: non-human-reviewed content must require human review")
    if row.get("index_in_production") and status not in INDEXABLE_STATUSES:
        error(f"{label}: indexed content has non-indexable status {status!r}")


def validate_english(label: str, body: str) -> None:
    portuguese = re.compile(
        r"\b(?:não|usuário|evidências|perguntas|quando aplicar|como responder|fontes relacionadas)\b",
        re.IGNORECASE,
    )
    match = portuguese.search(body)
    if match:
        error(f"{label}: canonical body appears non-English near {match.group(0)!r}")


def normalized_prose_blocks(path: Path, body: str) -> list[str]:
    blocks = []
    for block in re.split(r"\n\s*\n", body):
        normalized = re.sub(r"\s+", " ", block.strip().casefold())
        if len(normalized) >= 100 and not normalized.startswith("#"):
            blocks.append(normalized)
    return blocks


def main() -> int:
    required = (
        "README.md", "INDEX.md", "RETRIEVAL_CONTRACT.md", "CHUNKING_SPEC.md",
        "COVERAGE_MATRIX.md", "COVERAGE_GAPS.jsonl", "COVERAGE_EXPANSION_REPORT.md",
        "source_registry.jsonl", "concept_registry.jsonl", "document_registry.jsonl",
        "schemas/topic.schema.json", "schemas/knowledge.schema.json",
        "schemas/playbook.schema.json", "schemas/quote.schema.json",
        "schemas/source.schema.json", "non_indexed/system_prompt_candidates.md",
        "non_indexed/security_gate_candidates.md", "migration/MIGRATION_BASELINE.md",
        "migration/FILE_MAPPING.jsonl", "migration/MIGRATION_REPORT.md",
    )
    for item in required:
        if not (RAG / item).is_file():
            error(f"missing required file: {item}")
    for directory in ("sources/original", "sources/open_access", "sources/external_references", "sources/derived_notes"):
        if not (RAG / directory).is_dir():
            error(f"missing source boundary directory: {directory}")

    # Syntax-check every current JSON/JSONL file, including archived history.
    jsonl_cache: dict[Path, list[dict]] = {}
    for path in sorted(RAG.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f"{relative(path)}: invalid JSON: {exc}")
    for path in sorted(RAG.rglob("*.jsonl")):
        jsonl_cache[path] = load_jsonl(path)

    source_rows = jsonl_cache.get(RAG / "source_registry.jsonl", [])
    source_ids = [row.get("source_id") for row in source_rows]
    for duplicate in (item for item, count in Counter(source_ids).items() if count > 1):
        error(f"duplicate source_id: {duplicate}")
    sources = {row.get("source_id"): row for row in source_rows}
    for row in source_rows:
        sid = row.get("source_id")
        if not isinstance(sid, str) or not SOURCE_ID.fullmatch(sid):
            error(f"source registry: invalid source_id {sid!r}")
            continue
        require_fields(sid, row, ("title", "authors", "publication_year", "source_type", "url", "language", "topics", "verification_status", "requires_human_review", "active", "used_in_production_documents"))
        parsed = urlparse(str(row.get("url", "")))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            error(f"{sid}: invalid source URL")
        if row.get("active") and row.get("verification_status") not in ACTIVE_SOURCE_STATUSES:
            error(f"{sid}: active source lacks an allowed verification status")

    topic_paths = sorted(CANONICAL.glob("*/topic.yaml"))
    topic_meta: dict[str, dict] = {}
    for path in topic_paths:
        try:
            metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            error(f"{relative(path)}: invalid YAML: {exc}")
            continue
        if not isinstance(metadata, dict):
            error(f"{relative(path)}: topic YAML is not an object")
            continue
        tid = metadata.get("topic_id")
        if not isinstance(tid, str) or not KEBAB.fullmatch(tid):
            error(f"{relative(path)}: invalid or translated topic_id {tid!r}")
            continue
        if tid != path.parent.name:
            error(f"{relative(path)}: topic_id does not match directory")
        if tid in topic_meta:
            error(f"duplicate topic_id: {tid}")
        topic_meta[tid] = metadata
        require_fields(relative(path), metadata, ("title", "description", "status", "requires_human_review", "language", "related_topics", "retrieval_terms", "concept_ids", "playbook_ids", "quote_file"))
        validate_status(relative(path), metadata)
        if metadata.get("language") != "en":
            error(f"{relative(path)}: canonical topic language must be en")
        if len(metadata.get("retrieval_terms", [])) < 4:
            error(f"{relative(path)}: topic lacks retrieval value")

    canonical_topic_dirs = {path.name for path in CANONICAL.iterdir() if path.is_dir()}
    if canonical_topic_dirs != set(topic_meta):
        error(f"canonical topic directories do not match topic.yaml IDs: {sorted(canonical_topic_dirs ^ set(topic_meta))}")

    documents: dict[str, tuple[Path, dict, str]] = {}
    concepts: dict[str, tuple[Path, dict]] = {}
    playbooks: dict[str, tuple[Path, dict]] = {}
    prose: dict[str, list[str]] = defaultdict(list)
    canonical_filenames: list[str] = []

    for path in sorted(CANONICAL.glob("*/knowledge/*.md")):
        loaded = load_frontmatter(path)
        if loaded is None:
            continue
        metadata, body = loaded
        label = relative(path)
        document_id = metadata.get("id")
        concept_id = metadata.get("concept_id")
        topic_id = metadata.get("topic_id")
        require_fields(label, metadata, ("id", "topic_id", "concept_id", "title", "document_type", "language", "source_ids", "supported_claims", "evidence_level", "status", "requires_human_review", "index_in_production", "risk_level", "retrieval_terms", "related_concepts"))
        validate_status(label, metadata)
        if not isinstance(document_id, str) or not DOC_ID.fullmatch(document_id) or not document_id.startswith("kd-"):
            error(f"{label}: invalid knowledge document ID {document_id!r}")
        elif document_id in documents:
            error(f"duplicate document ID: {document_id}")
        else:
            documents[document_id] = (path, metadata, body)
        if not isinstance(concept_id, str) or not KEBAB.fullmatch(concept_id):
            error(f"{label}: invalid or translated concept_id {concept_id!r}")
        elif concept_id in concepts:
            error(f"duplicate concept_id: {concept_id}")
        else:
            concepts[concept_id] = (path, metadata)
        if topic_id not in topic_meta or path.parents[1].name != topic_id:
            error(f"{label}: invalid topic relationship")
        if metadata.get("document_type") != "knowledge" or metadata.get("language") != "en":
            error(f"{label}: canonical knowledge type/language mismatch")
        if len(metadata.get("source_ids", [])) < 2 or len(set(metadata.get("source_ids", []))) != len(metadata.get("source_ids", [])):
            error(f"{label}: knowledge must have at least two distinct sources")
        for sid in metadata.get("source_ids", []):
            if sid not in sources:
                error(f"{label}: missing source_id {sid}")
            elif not sources[sid].get("active"):
                error(f"{label}: production knowledge uses inactive source {sid}")
        for claim in metadata.get("supported_claims", []):
            if not isinstance(claim, dict) or not claim.get("claim_id") or not claim.get("source_ids") or not claim.get("evidence_strength"):
                error(f"{label}: malformed supported claim")
            elif not set(claim["source_ids"]) <= set(metadata.get("source_ids", [])):
                error(f"{label}: claim source not declared at document level")
        if len(metadata.get("retrieval_terms", [])) < 4:
            error(f"{label}: knowledge lacks retrieval value")
        for heading in KNOWLEDGE_HEADINGS:
            if heading not in body:
                error(f"{label}: missing section {heading}")
        if re.search(r"\b(?:Alfred|Feedbacker)\b", body):
            error(f"{label}: knowledge contains agent instructions")
        validate_english(label, body)
        canonical_filenames.append(path.name)
        for block in normalized_prose_blocks(path, body):
            prose[block].append(label)

    for path in sorted(CANONICAL.glob("*/playbooks/*.md")):
        loaded = load_frontmatter(path)
        if loaded is None:
            continue
        metadata, body = loaded
        label = relative(path)
        document_id = metadata.get("id")
        playbook_id = metadata.get("playbook_id")
        topic_id = metadata.get("topic_id")
        require_fields(label, metadata, ("id", "topic_id", "playbook_id", "title", "document_type", "language", "related_concept_ids", "status", "requires_human_review", "index_in_production", "risk_level", "trigger_phrases"))
        validate_status(label, metadata)
        if not isinstance(document_id, str) or not DOC_ID.fullmatch(document_id) or not document_id.startswith("pb-"):
            error(f"{label}: invalid playbook document ID {document_id!r}")
        elif document_id in documents:
            error(f"duplicate document ID: {document_id}")
        else:
            documents[document_id] = (path, metadata, body)
        if not isinstance(playbook_id, str) or not KEBAB.fullmatch(playbook_id):
            error(f"{label}: invalid or translated playbook_id {playbook_id!r}")
        elif playbook_id in playbooks:
            error(f"duplicate playbook_id: {playbook_id}")
        else:
            playbooks[playbook_id] = (path, metadata)
        if topic_id not in topic_meta or path.parents[1].name != topic_id:
            error(f"{label}: invalid topic relationship")
        if metadata.get("document_type") != "playbook" or metadata.get("language") != "en":
            error(f"{label}: canonical playbook type/language mismatch")
        if len(metadata.get("related_concept_ids", [])) < 1:
            error(f"{label}: playbook has no related concept")
        if len(metadata.get("trigger_phrases", [])) < 3:
            error(f"{label}: playbook lacks retrieval value")
        word_count = len(re.findall(r"\b\w+\b", body))
        if not 300 <= word_count <= 900:
            error(f"{label}: playbook body outside 300–900 word safety proxy: {word_count}")
        for heading in PLAYBOOK_HEADINGS:
            if heading not in body:
                error(f"{label}: missing section {heading}")
        validate_english(label, body)
        canonical_filenames.append(path.name)
        for block in normalized_prose_blocks(path, body):
            prose[block].append(label)

    for duplicate in (name for name, count in Counter(canonical_filenames).items() if count > 1):
        error(f"duplicate canonical filename: {duplicate}")
    for block, paths in prose.items():
        if len(paths) > 1:
            error(f"repeated canonical prose in {paths}: {block[:100]}…")

    concept_ids = set(concepts)
    playbook_ids = set(playbooks)
    for topic_id, metadata in topic_meta.items():
        for related in metadata.get("related_topics", []):
            if related not in topic_meta or related == topic_id:
                error(f"topic {topic_id}: invalid related topic {related}")
        actual_concepts = {cid for cid, (_, meta) in concepts.items() if meta.get("topic_id") == topic_id}
        actual_playbooks = {pid for pid, (_, meta) in playbooks.items() if meta.get("topic_id") == topic_id}
        if set(metadata.get("concept_ids", [])) != actual_concepts:
            error(f"topic {topic_id}: concept_ids do not match files")
        if set(metadata.get("playbook_ids", [])) != actual_playbooks:
            error(f"topic {topic_id}: playbook_ids do not match files")
        quote_file = metadata.get("quote_file")
        if quote_file is not None and not (CANONICAL / topic_id / quote_file).is_file():
            error(f"topic {topic_id}: missing quote_file {quote_file}")

    for _, metadata in concepts.values():
        for related in metadata.get("related_concepts", []):
            if related not in concept_ids:
                error(f"concept {metadata.get('concept_id')}: missing related concept {related}")
    for _, metadata in playbooks.values():
        for related in metadata.get("related_concept_ids", []):
            if related not in concept_ids:
                error(f"playbook {metadata.get('playbook_id')}: missing related concept {related}")

    quote_rows: list[dict] = []
    for path in sorted(CANONICAL.glob("*/quotes/*.jsonl")):
        topic_id = path.parents[1].name
        if path.name != f"{topic_id}.jsonl":
            error(f"{relative(path)}: quote file is outside its topic naming contract")
        for row in jsonl_cache.get(path, []):
            quote_rows.append(row)
            if row.get("verification_status") not in ALLOWED_QUOTE_STATUSES:
                error(f"{relative(path)}: active quote lacks allowed verification")
            if row.get("topic_id") != topic_id:
                error(f"{relative(path)}: quote topic mismatch")
            if row.get("source_id") not in sources:
                error(f"{relative(path)}: quote source does not exist")
            for concept_id in row.get("concept_ids", []):
                if concept_id not in concept_ids:
                    error(f"{relative(path)}: quote concept does not exist: {concept_id}")

    concept_rows = jsonl_cache.get(RAG / "concept_registry.jsonl", [])
    if len(concept_rows) != len(concepts):
        error("concept registry count does not match canonical concepts")
    concept_registry = {row.get("concept_id"): row for row in concept_rows}
    if set(concept_registry) != concept_ids:
        error("concept registry IDs do not match canonical concepts")
    for concept_id, row in concept_registry.items():
        path, metadata = concepts.get(concept_id, (None, {}))
        if row.get("topic_id") != metadata.get("topic_id") or row.get("canonical_document_id") != metadata.get("id"):
            error(f"concept registry mismatch for {concept_id}")
        if set(row.get("source_ids", [])) != set(metadata.get("source_ids", [])):
            error(f"concept registry source mismatch for {concept_id}")
        for pid in row.get("related_playbook_ids", []):
            if pid not in playbook_ids:
                error(f"concept registry {concept_id}: missing playbook {pid}")

    registry_rows = jsonl_cache.get(RAG / "document_registry.jsonl", [])
    registry = {row.get("document_id"): row for row in registry_rows}
    if len(registry) != len(registry_rows):
        error("document registry contains duplicate IDs")
    if set(registry) != set(documents):
        error("document registry IDs do not match canonical files")
    for document_id, row in registry.items():
        path, metadata, _ = documents.get(document_id, (None, {}, ""))
        expected_path = relative(path) if path else ""
        if row.get("path") != expected_path:
            error(f"document registry path mismatch for {document_id}")
        if not (RAG / str(row.get("path", ""))).is_file():
            error(f"document registry path does not exist for {document_id}")
        if row.get("document_type") != metadata.get("document_type") or row.get("topic_id") != metadata.get("topic_id"):
            error(f"document registry metadata mismatch for {document_id}")
        if row.get("concept_id") != metadata.get("concept_id") or row.get("playbook_id") != metadata.get("playbook_id"):
            error(f"document registry unit ID mismatch for {document_id}")
        if row.get("status") != metadata.get("status") or row.get("index_in_production") is not True:
            error(f"document registry editorial mismatch for {document_id}")
        if any(part in Path(row.get("path", "")).parts for part in ("archive", "migration", "non_indexed", "sources", "feedbacker", "safety")):
            error(f"forbidden production path in registry: {row.get('path')}")

    expected_source_usage: dict[str, set[str]] = {sid: set() for sid in sources}
    for document_id, (_, metadata, _) in documents.items():
        if metadata.get("document_type") == "knowledge":
            for sid in metadata.get("source_ids", []):
                expected_source_usage.setdefault(sid, set()).add(document_id)
    for sid, row in sources.items():
        if set(row.get("used_in_production_documents", [])) != expected_source_usage.get(sid, set()):
            error(f"{sid}: used_in_production_documents is out of sync")

    for path in (RAG / "non_indexed").glob("*.md"):
        loaded = load_frontmatter(path)
        if loaded and loaded[0].get("index_in_production") is not False:
            error(f"{relative(path)}: non-indexed file is not explicitly excluded")
    for path in (RAG / "archive").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^index_in_production:\s*true\s*$", text, re.MULTILINE):
            error(f"{relative(path)}: archived file claims production indexing")

    mapping_rows = jsonl_cache.get(RAG / "migration" / "FILE_MAPPING.jsonl", [])
    classification_rows = jsonl_cache.get(RAG / "migration" / "FILE_CLASSIFICATION.jsonl", [])
    replacement_paths = {
        row.get("path") for row in classification_rows
        if row.get("classification") == "replace_control_plane_and_archive"
    }
    for row in mapping_rows:
        if row.get("action") not in {"moved", "merged", "renamed", "archived", "removed"}:
            error(f"FILE_MAPPING: invalid action {row.get('action')!r}")
        target = resolve_migration_path(row.get("new_path"))
        if row.get("action") != "removed" and not target.exists():
            error(f"FILE_MAPPING: target does not exist: {row.get('new_path')}")
        original = resolve_migration_path(row.get("original_path"))
        if row.get("action") == "archived" and original.exists() and row.get("original_path") not in replacement_paths:
            error(f"FILE_MAPPING: archived original remains active: {row.get('original_path')}")

    for path in RAG.rglob("*"):
        if path.is_dir() and not any(path.iterdir()):
            error(f"empty directory: {relative(path)}")
    for path in RAG.rglob("*.pyc"):
        if not path.is_relative_to(RAG / "archive"):
            error(f"Python bytecode outside archive: {relative(path)}")

    result = {
        "status": "ok" if not ERRORS else "error",
        "architecture": "alfred_only_canonical_v1",
        "counts": {
            "topics": len(topic_meta),
            "knowledge_documents": len(concepts),
            "playbooks": len(playbooks),
            "active_quotes": len(quote_rows),
            "production_documents": len(registry),
            "sources": len(sources),
            "production_sources": sum(bool(row.get("used_in_production_documents")) for row in sources.values()),
            "migration_mapping_rows": len(mapping_rows),
        },
        "errors": ERRORS,
        "warnings": WARNINGS,
    }
    report_path = RAG / "migration" / "VALIDATION_REPORT.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
