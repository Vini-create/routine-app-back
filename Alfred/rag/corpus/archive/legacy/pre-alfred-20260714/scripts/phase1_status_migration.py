#!/usr/bin/env python3
"""Migra metadados legados para estados editoriais seguros da Fase 1.

Não modifica o corpo temático dos documentos. Cada mudança é registrada em
``rag/audit/phase1_status_migration.jsonl`` para permitir revisão e reversão a
partir do checkpoint da auditoria.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


RAG = Path(__file__).resolve().parents[1]
AUDIT_LOG = RAG / "audit" / "phase1_status_migration.jsonl"
DOCUMENT_ROOTS = ("knowledge", "playbooks", "cases", "safety")


def set_frontmatter_field(frontmatter: str, key: str, value: str) -> tuple[str, str | None]:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*$", re.MULTILINE)
    match = pattern.search(frontmatter)
    old = match.group(1).strip().strip('"\'') if match else None
    rendered = f'{key}: "{value}"' if value not in {"true", "false"} else f"{key}: {value}"
    if match:
        return pattern.sub(rendered, frontmatter, count=1), old
    return frontmatter.rstrip() + "\n" + rendered + "\n", old


def migrate_markdown(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"frontmatter ausente: {path.relative_to(RAG)}")
    frontmatter = match.group(1)
    frontmatter, old_status = set_frontmatter_field(frontmatter, "status", "generated")
    frontmatter, old_review = set_frontmatter_field(frontmatter, "requires_human_review", "true")
    frontmatter, old_index = set_frontmatter_field(frontmatter, "index_eligible", "false")
    updated = f"---\n{frontmatter.rstrip()}\n---\n" + text[match.end():]
    path.write_text(updated, encoding="utf-8")
    return {
        "path": path.relative_to(RAG).as_posix(),
        "artifact_type": "markdown_document",
        "old_status": old_status,
        "new_status": "generated",
        "old_requires_human_review": old_review,
        "new_requires_human_review": True,
        "old_index_eligible": old_index,
        "new_index_eligible": False,
        "reason": "model_generated_content_not_human_reviewed",
    }


def rewrite_jsonl(path: Path, transform) -> list[dict]:
    rows = []
    audit = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        before = dict(row)
        transform(row)
        rows.append(row)
        audit.append(
            {
                "path": path.relative_to(RAG).as_posix(),
                "line": number,
                "artifact_type": "jsonl_record",
                "record_id": row.get("document_id")
                or row.get("source_id")
                or row.get("quote_id")
                or row.get("technique_id")
                or row.get("scenario_id")
                or row.get("question_id")
                or row.get("topic"),
                "old_status": before.get("status"),
                "new_status": row.get("status"),
                "old_verification_status": before.get("verification_status"),
                "new_verification_status": row.get("verification_status"),
                "new_requires_human_review": row.get("requires_human_review"),
                "new_active": row.get("active"),
                "new_index_eligible": row.get("index_eligible"),
                "reason": "phase1_precautionary_demotion",
            }
        )
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    return audit


def main() -> None:
    if AUDIT_LOG.exists():
        raise SystemExit(
            "MIGRAÇÃO DA FASE 1 JÁ REGISTRADA: execução repetida sobrescreveria "
            "o estado anterior capturado no log."
        )
    changes = []
    for root_name in DOCUMENT_ROOTS:
        for path in sorted((RAG / root_name).rglob("*.md")):
            changes.append(migrate_markdown(path))

    def document(row: dict) -> None:
        row["status"] = "generated"
        row["requires_human_review"] = True
        row["index_eligible"] = False

    changes.extend(rewrite_jsonl(RAG / "document_registry.jsonl", document))

    def source(row: dict) -> None:
        if "prior_verification_status" not in row:
            row["prior_verification_status"] = row.get("verification_status")
        row["verification_status"] = "requires_human_review"
        row["requires_human_review"] = True
        row["active"] = False

    changes.extend(rewrite_jsonl(RAG / "source_registry.jsonl", source))

    for path in sorted((RAG / "quotes").glob("*.jsonl")):
        def quote(row: dict) -> None:
            if "prior_verification_status" not in row:
                row["prior_verification_status"] = row.get("verification_status")
            row["status"] = "generated"
            row["verification_status"] = "attribution_uncertain"
            row["requires_human_review"] = True
            row["active"] = False

        changes.extend(rewrite_jsonl(path, quote))

    for directory in ("techniques", "evaluation"):
        for path in sorted((RAG / directory).glob("*.jsonl")):
            def generated_record(row: dict) -> None:
                row["status"] = "generated"
                row["requires_human_review"] = True
                row["active"] = False

            changes.extend(rewrite_jsonl(path, generated_record))

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_LOG.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in changes),
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "changes_logged": len(changes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
