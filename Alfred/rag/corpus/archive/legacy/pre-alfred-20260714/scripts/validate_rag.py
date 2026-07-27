#!/usr/bin/env python3
"""Valida estrutura, estados editoriais e integridade referencial da base RAG."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import yaml


RAG = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []
DOCUMENT_STATUSES = {
    "draft", "generated", "research_verified", "machine_audited",
    "human_reviewed", "deprecated", "quarantined",
}
SOURCE_STATUSES = {
    "verified_primary", "verified_official_repository",
    "verified_reliable_secondary", "metadata_incomplete",
    "requires_human_review", "invalid",
}
QUOTE_STATUSES = {
    "verified_primary_source", "verified_official_edition",
    "verified_reliable_secondary", "translation_requires_review",
    "attribution_uncertain", "apocryphal", "removed",
}
ACTIVE_SOURCE_STATUSES = {
    "verified_primary", "verified_official_repository", "verified_reliable_secondary",
}
ACTIVE_QUOTE_STATUSES = {
    "verified_primary_source", "verified_official_edition", "verified_reliable_secondary",
}


def error(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            error(f"{path.relative_to(RAG)}:{number}: JSON inválido: {exc}")
            continue
        if not isinstance(value, dict):
            error(f"{path.relative_to(RAG)}:{number}: registro não é objeto")
        else:
            rows.append(value)
    return rows


def load_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        error(f"{path.relative_to(RAG)}: frontmatter ausente ou mal delimitado")
        return None
    try:
        value = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        error(f"{path.relative_to(RAG)}: YAML inválido: {exc}")
        return None
    if not isinstance(value, dict):
        error(f"{path.relative_to(RAG)}: frontmatter não é objeto")
        return None
    return value


def validate_editorial_state(label: str, row: dict, eligibility_key: str = "index_eligible") -> None:
    status = row.get("status")
    if status not in DOCUMENT_STATUSES:
        error(f"{label}: status editorial inválido ou ausente: {status!r}")
    if not isinstance(row.get("requires_human_review"), bool):
        error(f"{label}: requires_human_review deve ser booleano")
    eligible = row.get(eligibility_key)
    if not isinstance(eligible, bool):
        error(f"{label}: {eligibility_key} deve ser booleano")
    if eligible and status not in {"machine_audited", "human_reviewed"}:
        error(f"{label}: conteúdo {status!r} não pode ser elegível/ativo")
    # Esta reconstrução é executada por modelo; promoção humana é sempre externa.
    if status == "human_reviewed":
        error(f"{label}: human_reviewed não pode ser atribuído por este processo")
    if status != "human_reviewed" and row.get("requires_human_review") is not True:
        error(f"{label}: conteúdo sem revisão humana deve exigir revisão humana")


def normalize_question(value: str) -> str:
    """Normaliza apenas para detectar reaproveitamento literal entre documentos."""
    return re.sub(r"\s+", " ", value.strip().casefold())


def main() -> int:
    required = [
        "README.md", "INDEX.md", "source_registry.jsonl", "document_registry.jsonl",
        "QUALITY_REPORT.md", "REVIEW_REQUIRED.md", "MISSING_TOPICS.md",
        "AUDIT_BASELINE.md", "audit/baseline_file_inventory.jsonl",
        "audit/phase1_status_migration.jsonl",
        "schemas/knowledge_document.schema.json", "schemas/playbook.schema.json",
        "schemas/quote.schema.json", "schemas/case.schema.json", "schemas/source.schema.json",
        "schemas/technique.schema.json",
    ]
    for rel in required:
        if not (RAG / rel).exists():
            error(f"arquivo obrigatório ausente: {rel}")

    for path in RAG.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f"{path.relative_to(RAG)}: JSON inválido: {exc}")
    jsonl = {path: load_jsonl(path) for path in RAG.rglob("*.jsonl")}
    technique_ids = {
        row.get("technique_id")
        for path, rows in jsonl.items() if path.parent.name == "techniques"
        for row in rows if row.get("technique_id")
    }

    sources = jsonl.get(RAG / "source_registry.jsonl", [])
    source_ids = [row.get("source_id") for row in sources]
    for duplicate in [item for item, count in Counter(source_ids).items() if count > 1]:
        error(f"source_id duplicado: {duplicate}")
    source_by_id = {row.get("source_id"): row for row in sources}
    for row in sources:
        sid = row.get("source_id", "<sem-id>")
        for key in ("title", "authors", "publication_year", "source_type", "url", "topics", "verification_status"):
            if row.get(key) in (None, "", []):
                error(f"fonte {sid}: campo obrigatório vazio: {key}")
        if row.get("verification_status") not in SOURCE_STATUSES:
            error(f"fonte {sid}: verification_status inválido")
        if not isinstance(row.get("requires_human_review"), bool):
            error(f"fonte {sid}: requires_human_review deve ser booleano")
        if not isinstance(row.get("active"), bool):
            error(f"fonte {sid}: active deve ser booleano")
        if row.get("active") and row.get("verification_status") not in ACTIVE_SOURCE_STATUSES:
            error(f"fonte {sid}: fonte ativa sem verificação suficiente")
        if row.get("verification_status") in ACTIVE_SOURCE_STATUSES:
            for key in ("verification_url", "accessed_at", "verified_by", "scope_limitations"):
                if row.get(key) in (None, "", []):
                    error(f"fonte {sid}: verificação ativa sem {key}")
        parsed = urlparse(str(row.get("url", "")))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            error(f"fonte {sid}: URL malformada")
        doi = row.get("doi", "")
        if doi and not re.match(r"^10\.\d{4,9}/\S+$", doi):
            error(f"fonte {sid}: DOI malformado: {doi}")

    roots = [RAG / name for name in ("knowledge", "playbooks", "cases", "safety")]
    documents: dict[str, tuple[Path, dict]] = {}
    knowledge_questions: dict[str, str] = {}
    for root in roots:
        for path in sorted(root.rglob("*.md")):
            fm = load_frontmatter(path)
            if fm is None:
                continue
            key = "case_id" if path.is_relative_to(RAG / "cases") else "id"
            document_id = fm.get(key)
            if not isinstance(document_id, str) or not document_id:
                error(f"{path.relative_to(RAG)}: {key} ausente")
                continue
            if document_id in documents:
                error(f"ID duplicado {document_id}: {documents[document_id][0]} e {path}")
            documents[document_id] = (path, fm)
            validate_editorial_state(path.relative_to(RAG).as_posix(), fm)
            for sid in fm.get("source_ids", []):
                if sid not in source_by_id:
                    error(f"{path.relative_to(RAG)}: source_id inexistente: {sid}")
            if path.is_relative_to(RAG / "knowledge"):
                for field in ("title", "document_type", "domain", "agents", "source_ids", "supported_claims", "retrieval_terms", "decision_questions", "risk_level"):
                    if field not in fm:
                        error(f"{path.relative_to(RAG)}: campo ausente: {field}")
                questions = fm.get("decision_questions", [])
                if not isinstance(questions, list) or len(questions) != 3:
                    error(f"{path.relative_to(RAG)}: decision_questions deve conter exatamente três perguntas")
                else:
                    local_questions: set[str] = set()
                    for question in questions:
                        if not isinstance(question, str) or len(question.strip()) < 20 or not question.rstrip().endswith("?"):
                            error(f"{path.relative_to(RAG)}: pergunta de decisão malformada: {question!r}")
                            continue
                        normalized = normalize_question(question)
                        if normalized in local_questions:
                            error(f"{path.relative_to(RAG)}: pergunta de decisão repetida no documento: {question}")
                        local_questions.add(normalized)
                        if normalized in knowledge_questions:
                            error(f"{path.relative_to(RAG)}: pergunta de decisão repetida de {knowledge_questions[normalized]}: {question}")
                        knowledge_questions[normalized] = path.relative_to(RAG).as_posix()
                knowledge_sources = fm.get("source_ids", [])
                if not isinstance(knowledge_sources, list) or len(set(knowledge_sources)) < 2:
                    error(f"{path.relative_to(RAG)}: knowledge auditado deve usar ao menos duas fontes distintas")
                for claim in fm.get("supported_claims", []):
                    if not isinstance(claim, dict) or not claim.get("claim_id") or not claim.get("source_ids") or not claim.get("evidence_strength"):
                        error(f"{path.relative_to(RAG)}: supported_claim malformado: {claim}")
                        continue
                    for sid in claim.get("source_ids", []):
                        source = source_by_id.get(sid)
                        if not source:
                            error(f"{path.relative_to(RAG)}: claim usa fonte inexistente {sid}")
                        elif fm.get("status") == "machine_audited" and not source.get("active"):
                            error(f"{path.relative_to(RAG)}: claim auditado usa fonte inativa {sid}")
                if fm.get("status") == "machine_audited":
                    body = path.read_text(encoding="utf-8")
                    for heading in ("## Definição operacional", "## Mapeamento das evidências", "## Decisão que este conhecimento apoia", "## Perguntas úteis para decidir", "## Processo de aplicação", "## Explicações alternativas", "## Exemplo contextualizado", "## Limitações"):
                        if heading not in body:
                            error(f"{path.relative_to(RAG)}: seção auditada ausente: {heading}")
                    for question in questions:
                        if isinstance(question, str) and f"- {question}" not in body:
                            error(f"{path.relative_to(RAG)}: pergunta do frontmatter ausente no corpo: {question}")
            if path.is_relative_to(RAG / "playbooks") and fm.get("status") == "machine_audited":
                if not fm.get("trigger_phrases"):
                    error(f"{path.relative_to(RAG)}: playbook auditado sem trigger_phrases")
                for related in fm.get("related_knowledge", []):
                    if related not in documents:
                        error(f"{path.relative_to(RAG)}: related_knowledge inexistente {related}")
                for technique in fm.get("candidate_techniques", []):
                    if technique not in technique_ids:
                        error(f"{path.relative_to(RAG)}: candidate_technique inexistente {technique}")
                body = path.read_text(encoding="utf-8")
                agents = fm.get("agents", [])
                if agents == ["alfred"]:
                    for heading in ("## Critérios de ativação", "## Situações semelhantes que não devem ativá-lo", "## Árvore de decisão", "## Quando não fazer pergunta", "## Quando não oferecer solução", "## Quando encerrar ou mudar de fluxo"):
                        if heading not in body:
                            error(f"{path.relative_to(RAG)}: seção Alfred ausente: {heading}")
                if agents == ["feedbacker"]:
                    for heading in ("## Observação", "## Padrão", "## Hipótese e confiança", "## Evidência favorável", "## Evidência contrária", "## Dados ausentes", "## Critério de revisão"):
                        if heading not in body:
                            error(f"{path.relative_to(RAG)}: seção Feedbacker ausente: {heading}")
            if path.is_relative_to(RAG / "safety") and fm.get("deterministic_rule_candidate") is not True:
                error(f"{path.relative_to(RAG)}: regra de segurança sem marca determinística")

    decision_keys = []
    valid_retrieval_ids = set(documents) | technique_ids
    for document_id, (path, fm) in documents.items():
        if not path.is_relative_to(RAG / "cases") or fm.get("status") != "machine_audited":
            continue
        for field in ("observed_facts", "possible_hypotheses", "missing_information", "relevant_knowledge", "relevant_playbooks", "incorrect_retrievals", "risk_assessment", "ideal_behavior", "acceptable_variations", "must_avoid", "decision_key"):
            if field not in fm:
                error(f"{path.relative_to(RAG)}: caso auditado sem {field}")
        decision_keys.append(fm.get("decision_key"))
        for related in fm.get("relevant_knowledge", []):
            target = documents.get(related)
            if not target or not target[0].is_relative_to(RAG / "knowledge"):
                error(f"{path.relative_to(RAG)}: relevant_knowledge inválido {related}")
        for related in fm.get("relevant_playbooks", []):
            target = documents.get(related)
            if not target or not target[0].is_relative_to(RAG / "playbooks"):
                error(f"{path.relative_to(RAG)}: relevant_playbook inválido {related}")
        for related in fm.get("incorrect_retrievals", []):
            if related not in valid_retrieval_ids:
                error(f"{path.relative_to(RAG)}: incorrect_retrieval inexistente {related}")
        risk = fm.get("risk_assessment")
        if not isinstance(risk, dict) or risk.get("level") != fm.get("risk_level") or not risk.get("reason"):
            error(f"{path.relative_to(RAG)}: risk_assessment inconsistente")
    for duplicate in [item for item, count in Counter(decision_keys).items() if item and count > 1]:
        error(f"decision_key de caso duplicada: {duplicate}")

    registry = jsonl.get(RAG / "document_registry.jsonl", [])
    registry_ids = [row.get("document_id") for row in registry]
    for duplicate in [item for item, count in Counter(registry_ids).items() if count > 1]:
        error(f"document_registry: ID duplicado: {duplicate}")
    if set(registry_ids) != set(documents):
        error(f"document_registry divergente: faltantes={sorted(set(documents) - set(registry_ids))}, obsoletos={sorted(set(registry_ids) - set(documents))}")
    for row in registry:
        document_id = row.get("document_id", "<sem-id>")
        validate_editorial_state(f"document_registry:{document_id}", row)
        path = RAG / str(row.get("path", ""))
        if not path.is_file():
            error(f"document_registry:{document_id}: caminho inexistente")
        elif document_id in documents:
            fm = documents[document_id][1]
            for field in ("status", "requires_human_review", "index_eligible"):
                if row.get(field) != fm.get(field):
                    error(f"document_registry:{document_id}: {field} diverge do frontmatter")
        for sid in row.get("source_ids", []):
            if sid not in source_by_id:
                error(f"document_registry:{document_id}: fonte inexistente {sid}")

    structured_ids: list[str] = []
    quote_originals: list[str] = []
    for path, rows in jsonl.items():
        area = path.parent.name
        if area not in {"quotes", "techniques", "evaluation"}:
            continue
        for number, row in enumerate(rows, 1):
            label = f"{path.relative_to(RAG)}:{number}"
            validate_editorial_state(label, row, "active")
            candidate_id = row.get("quote_id") or row.get("technique_id") or row.get("scenario_id") or row.get("question_id")
            if candidate_id:
                structured_ids.append(candidate_id)
            for sid in row.get("source_ids", []) + row.get("expected_sources", []) + row.get("expected_source_ids", []):
                if sid not in source_by_id:
                    error(f"{label}: fonte inexistente {sid}")
            if area == "quotes":
                quote_originals.append(re.sub(r"\W+", " ", row.get("original_quote", "").lower()).strip())
                if row.get("source_id") not in source_by_id:
                    error(f"{label}: source_id inexistente")
                if row.get("verification_status") not in QUOTE_STATUSES:
                    error(f"{label}: verification_status de citação inválido")
                if row.get("active") and row.get("verification_status") not in ACTIVE_QUOTE_STATUSES:
                    error(f"{label}: citação ativa sem verificação suficiente")
                if len(row.get("original_quote", "").split()) > 25:
                    error(f"{label}: citação excede 25 palavras")
            if area == "techniques":
                for field in ("official_name", "name_pt_br", "technique_origin", "definition", "proposed_mechanism", "evidence_level", "supported_claims", "source_ids", "use_when", "preconditions", "contraindications", "implementation_steps", "example", "applicable_agents"):
                    if row.get(field) in (None, "", []):
                        error(f"{label}: técnica sem campo obrigatório {field}")
                for sid in row.get("source_ids", []):
                    source = source_by_id.get(sid)
                    if row.get("status") == "machine_audited" and source and not source.get("active"):
                        error(f"{label}: técnica auditada usa fonte inativa {sid}")
    for duplicate in [item for item, count in Counter(structured_ids).items() if count > 1]:
        error(f"ID estruturado duplicado: {duplicate}")
    for duplicate in [item for item, count in Counter(quote_originals).items() if item and count > 1]:
        error(f"citação original duplicada: {duplicate}")

    quarantine_registry = RAG / "quarantine" / "registry.jsonl"
    if quarantine_registry.exists():
        for row in load_jsonl(quarantine_registry):
            if row.get("active") or row.get("index_eligible"):
                error(f"quarentena: item ativo/elegível: {row}")

    corpus = "\n".join(path.read_text(encoding="utf-8") for root in roots for path in root.rglob("*.md"))
    for phrase in ("cura garantida", "basta querer", "substitui seu médico", "21 dias para qualquer hábito"):
        if phrase.casefold() in corpus.casefold():
            error(f"frase proibida encontrada: {phrase}")

    counts = {
        "markdown_documents": len(documents),
        "registered_documents": len(registry),
        "sources": len(sources),
        "quotes": sum(len(rows) for path, rows in jsonl.items() if path.parent.name == "quotes"),
        "techniques": sum(len(rows) for path, rows in jsonl.items() if path.parent.name == "techniques"),
        "evaluation_records": sum(len(rows) for path, rows in jsonl.items() if path.parent.name == "evaluation"),
        "index_eligible_documents": sum(bool(row.get("index_eligible")) for row in registry),
        "active_sources": sum(bool(row.get("active")) for row in sources),
    }
    result = {"status": "ok" if not ERRORS else "failed", "validated_through_phase": 8, "counts": counts, "errors": ERRORS, "warnings": WARNINGS}
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (RAG / "audit" / "validation_latest.json").write_text(rendered, encoding="utf-8")
    (RAG / "audit" / "phase8_structural_validation.json").write_text(rendered, encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
