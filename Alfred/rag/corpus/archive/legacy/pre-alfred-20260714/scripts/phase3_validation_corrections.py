#!/usr/bin/env python3
"""Correções explícitas encontradas pelo gate de validação da Fase 3."""

import json
from pathlib import Path

RAG = Path(__file__).resolve().parents[1]
REGISTRY = RAG / "source_registry.jsonl"
LOG = RAG / "audit" / "phase3_validation_corrections.jsonl"
LIMITS = {
    "src-ii-2006": "Efeito médio de planos se–então não elimina heterogeneidade, falhas de execução nem necessidade de uma intenção prévia.",
    "src-intention-behavior-2006": "Mudança de intenção tem efeito médio limitado sobre comportamento; não autoriza inferir execução individual.",
    "src-sdt-techniques-2019": "Técnicas foram sintetizadas em intervenções de saúde; efeitos dependem de implementação e contexto.",
    "src-procrastination-steel-2007": "Preditores meta-analíticos são associações agregadas e não explicações causais de uma pessoa.",
}

if LOG.exists():
    raise SystemExit("Correções da Fase 3 já registradas.")
rows = [json.loads(line) for line in REGISTRY.read_text(encoding="utf-8").splitlines() if line]
changes = []
for row in rows:
    if row["source_id"] in LIMITS:
        changes.append({"source_id": row["source_id"], "old_scope_limitations": row.get("scope_limitations"), "new_scope_limitations": LIMITS[row["source_id"]]})
        row["scope_limitations"] = LIMITS[row["source_id"]]
REGISTRY.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
LOG.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in changes), encoding="utf-8")
print(json.dumps({"status": "ok", "corrected": len(changes)}))
