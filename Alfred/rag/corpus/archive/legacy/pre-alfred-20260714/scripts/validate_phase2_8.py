#!/usr/bin/env python3
"""Gate complementar de qualidade para o fechamento das Fases 2–8."""

import json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
import yaml

RAG=Path(__file__).resolve().parents[1]; errors=[]; warnings=[]
docs={}
paragraphs=defaultdict(list)
for root in ("knowledge","playbooks","cases","safety"):
    for path in (RAG/root).rglob("*.md"):
        text=path.read_text(encoding="utf-8"); fm=yaml.safe_load(text.split("---",2)[1]); did=fm.get("id") or fm.get("case_id"); docs[did]=fm
        if fm.get("status")!="machine_audited": continue
        for para in re.split(r"\n\s*\n",text.split("---",2)[-1]):
            norm=" ".join(para.split()).casefold()
            if len(norm)>=50 and not norm.startswith("#"): paragraphs[norm].append(path.relative_to(RAG).as_posix())
for para,paths in paragraphs.items():
    if len(paths)>1: errors.append(f"parágrafo literal repetido em conteúdo auditado ({len(paths)}): {para[:120]} — {paths}")

tech=[]
for path in (RAG/"techniques").glob("*.jsonl"):
    tech += [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]
expected={did for did,fm in docs.items() if fm.get("status")=="machine_audited"} | {row["technique_id"] for row in tech if row.get("status")=="machine_audited"}
scores=[json.loads(x) for x in (RAG/"DOCUMENT_QUALITY_SCORES.jsonl").read_text(encoding="utf-8").splitlines() if x]
ids=[row.get("document_id") for row in scores]
for duplicate in [x for x,n in Counter(ids).items() if n>1]: errors.append(f"score duplicado: {duplicate}")
if set(ids)!=expected: errors.append(f"cobertura de scores divergente: faltam={sorted(expected-set(ids))}, sobram={sorted(set(ids)-expected)}")
for row in scores:
    for key in ("specificity","traceability","actionability","retrieval_value","safety"):
        if row.get(key,0)<4: errors.append(f"{row.get('document_id')}: {key} abaixo de 4")
    if row.get("document_type") in {"knowledge","technique"} and row.get("evidence",0)<4: errors.append(f"{row.get('document_id')}: evidence abaixo de 4")

qrows=[json.loads(x) for x in (RAG/"quarantine"/"registry.jsonl").read_text(encoding="utf-8").splitlines() if x]
if any(row.get("active") or row.get("index_eligible") for row in qrows): errors.append("item de quarentena ativo ou elegível")
result={"status":"ok" if not errors else "failed","validated_through_phase":8,"machine_audited_units":len(expected),"quality_scores":len(scores),"repeated_paragraphs":sum(1 for paths in paragraphs.values() if len(paths)>1),"quarantine_records":len(qrows),"errors":errors,"warnings":warnings}
(RAG/"audit"/"phase8_quality_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2)); sys.exit(1 if errors else 0)
