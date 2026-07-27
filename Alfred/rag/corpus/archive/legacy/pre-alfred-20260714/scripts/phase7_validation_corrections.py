#!/usr/bin/env python3
"""Aplica correção de nomenclatura obrigatória encontrada no gate da Fase 7."""

import json
from pathlib import Path

RAG=Path(__file__).resolve().parents[1]
OLD=RAG/"playbooks"/"feedbacker"/"pb-f-confidence-guide.md"
NEW=RAG/"playbooks"/"feedbacker"/"CONFIDENCE_AND_EVIDENCE_GUIDE.md"
LOG=RAG/"audit"/"phase7_validation_corrections.jsonl"
if LOG.exists(): raise SystemExit("Correção já aplicada.")
OLD.rename(NEW)
rows=[json.loads(x) for x in (RAG/"document_registry.jsonl").read_text(encoding="utf-8").splitlines() if x]
for row in rows:
    if row.get("document_id")=="pb-f-confidence-guide": row["path"]="playbooks/feedbacker/CONFIDENCE_AND_EVIDENCE_GUIDE.md"
(RAG/"document_registry.jsonl").write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in rows),encoding="utf-8")
LOG.write_text(json.dumps({"document_id":"pb-f-confidence-guide","change":"required_filename","old_path":OLD.relative_to(RAG).as_posix(),"new_path":NEW.relative_to(RAG).as_posix()},ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"status":"ok","renamed":1}))
