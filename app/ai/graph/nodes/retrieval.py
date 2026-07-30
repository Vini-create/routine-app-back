"""Multilingual, hybrid and fail-closed RAG nodes."""

from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Mapping
from typing import Any

from langgraph.runtime import Runtime

from app.ai.domain.enums import InternalRoute
from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.nodes.entry import assess_prompt_injection
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.retrieval.hybrid import lexical_tokens
from app.ai.retrieval.sources import resolve_public_sources
from app.core.config import settings

KNOWN_TOPICS = frozenset(
    {
        "goals",
        "habits",
        "motivation",
        "physical-activity",
        "planning",
        "procrastination",
        "self-regulation",
        "sleep-and-recovery",
        "study-and-learning",
    }
)
TOPIC_PATTERNS = {
    "goals": re.compile(
        r"\b(?:meta|metas|objetivo|objetivos|goal|goals|target|objetivo|"
        r"objectifs?|deadline|prazo|prioridade)\b"
    ),
    "habits": re.compile(
        r"\b(?:habito|habitos|habit|habits|habitude|habitudes|rutina|routine|"
        r"rotina|repeticao|consistencia|streak)\b"
    ),
    "motivation": re.compile(
        r"\b(?:motivacao|motivation|motivacion|motivation|desanimo|sem vontade|"
        r"autonomia|recompensa|reward)\b"
    ),
    "physical-activity": re.compile(
        r"\b(?:atividade fisica|exercicio|treino|academia|caminhada|corrida|"
        r"physical activity|exercise|workout|entrenamiento|exercice)\b"
    ),
    "planning": re.compile(
        r"\b(?:planejamento|planejar|plano|planning|planificar|planification|"
        r"agenda|schedule|cronograma|organizar)\b"
    ),
    "procrastination": re.compile(
        r"\b(?:procrastin\w*|adiando|adiar|enrolando|nao consigo comecar|"
        r"cannot start|can t start|putting off|postergando|remettre a plus tard)\b"
    ),
    "self-regulation": re.compile(
        r"\b(?:autorregulacao|self regulation|autocontrole|self control|"
        r"monitoramento|feedback|revisao semanal|weekly review)\b"
    ),
    "sleep-and-recovery": re.compile(
        r"\b(?:sono|dormir|descanso|recuperacao|cansaco|fadiga|sleep|recovery|"
        r"fatigue|sommeil|repos|sueno)\b"
    ),
    "study-and-learning": re.compile(
        r"\b(?:estudo|estudar|aprendizagem|prova|study|learning|exam|"
        r"aprender|etude|apprentissage)\b"
    ),
}
MIN_RETRIEVAL_CONFIDENCE = 0.52
MIN_UNSCOPED_RETRIEVAL_CONFIDENCE = 0.58
MIN_RETRIEVAL_COVERAGE = 0.45


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _fold_topic_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


def _append_unique(values: list[str], value: str) -> list[str]:
    return values if value in values else [*values, value]


def _retrieval_topics(state: AgentState) -> list[str]:
    topics: list[str] = []
    for value in (
        *state.get("retrieval_topics", []),
        *state.get("required_context", []),
    ):
        normalized = str(value).strip().casefold().replace("_", "-")
        if normalized in KNOWN_TOPICS and normalized not in topics:
            topics.append(normalized)
    for habit in state.get("habits", [])[:10]:
        category = str(habit.get("category", "")).strip().casefold().replace("_", "-")
        if category in KNOWN_TOPICS and category not in topics:
            topics.append(category)
    recent_context = " ".join(
        str(message.get("content", ""))
        for message in state.get("recent_messages", [])[-4:]
        if isinstance(message, Mapping)
    )
    normalized_input = _fold_topic_text(
        " ".join(
            (
                state.get("normalized_input", state["original_input"]),
                state.get("conversation_summary", "")[:1_000],
                recent_context[:1_500],
            )
        )
    )
    for topic, pattern in TOPIC_PATTERNS.items():
        if pattern.search(normalized_input) and topic not in topics:
            topics.append(topic)
    return topics[:8]


def _build_query(state: AgentState) -> str:
    original = state.get("normalized_input", state["original_input"]).strip()
    topics = _retrieval_topics(state)
    # The query embedding consumes the original language. Canonical topic IDs
    # make referential follow-ups ("sources for that?") traceable to the recent
    # conversation without translating user content or inventing facts.
    suffix = f"\nRelevant topics: {', '.join(topics)}" if topics else ""
    return f"{original}{suffix}"[:2_000].strip()


def _rerank_document(
    document: dict[str, Any],
    *,
    query: str,
    topics: set[str],
) -> dict[str, Any]:
    metadata = dict(document.get("metadata", {}))
    dense_score = float(metadata.get("dense_score", 0.0))
    fusion_score = _clamp(float(metadata.get("fusion_score", 0.0)))
    lexical_score = max(0.0, float(metadata.get("lexical_score", 0.0)))

    # text-embedding-3-small cosine similarities for the curated corpus become
    # useful above roughly 0.20. Preserve the full remaining cosine range so
    # strong candidates still retain their relative ordering. This is an
    # internal relevance score, not a probability.
    semantic_relevance = _clamp((dense_score - 0.20) / 0.80)
    lexical_relevance = 1.0 - math.exp(-lexical_score)
    topic_match = 1.0 if document.get("topic") in topics else 0.0
    traceability = 1.0 if metadata.get("source_path") else 0.0
    rerank_score = _clamp(
        0.65 * semantic_relevance
        + 0.20 * fusion_score
        + 0.08 * lexical_relevance
        + 0.04 * topic_match
        + 0.03 * traceability
    )

    query_terms = set(lexical_tokens(query))
    document_terms = set(
        lexical_tokens(
            " ".join(
                (
                    str(document.get("title", "")),
                    str(document.get("topic", "")),
                    str(metadata.get("concept_id", "")),
                    str(document.get("content", "")),
                )
            )
        )
    )
    term_coverage = (
        len(query_terms & document_terms) / len(query_terms) if query_terms else 0.0
    )
    metadata["semantic_relevance"] = round(semantic_relevance, 6)
    metadata["term_coverage"] = round(term_coverage, 6)
    return {
        **document,
        "metadata": metadata,
        "rerank_score": round(rerank_score, 6),
    }


def _retrieval_quality(
    documents: list[dict[str, Any]],
    *,
    expected_topics: set[str],
) -> tuple[float, float, bool]:
    if not documents:
        return 0.0, 0.0, True
    scores = [float(document.get("rerank_score", 0.0)) for document in documents]
    top_score = scores[0]
    margin = max(0.0, top_score - scores[1]) if len(scores) > 1 else top_score
    traceability = sum(
        bool(document.get("metadata", {}).get("source_path"))
        for document in documents[:3]
    ) / min(3, len(documents))
    confidence = _clamp(0.82 * top_score + 0.10 * margin + 0.08 * traceability)

    knowledge = [
        document
        for document in documents[:4]
        if document.get("metadata", {}).get("document_type") == "knowledge"
    ]
    semantic_coverage = sum(
        float(document.get("metadata", {}).get("semantic_relevance", 0.0))
        for document in knowledge[:3]
    ) / max(1, min(3, len(knowledge)))
    evidence_count = min(1.0, len(knowledge) / 2)
    topic_alignment = (
        sum(document.get("topic") in expected_topics for document in knowledge[:3])
        / max(1, min(3, len(knowledge)))
        if expected_topics
        else 0.0
    )
    coverage = _clamp(
        0.62 * semantic_coverage
        + 0.23 * evidence_count
        + 0.15 * topic_alignment
    )
    confidence_floor = (
        MIN_RETRIEVAL_CONFIDENCE
        if expected_topics
        else MIN_UNSCOPED_RETRIEVAL_CONFIDENCE
    )
    insufficient = (
        not knowledge
        or confidence < confidence_floor
        or coverage < MIN_RETRIEVAL_COVERAGE
    )
    return round(confidence, 6), round(coverage, 6), insufficient


def _supporting_excerpt(content: str, *, max_characters: int = 900) -> str:
    sections = re.split(r"(?m)^## ", content)
    selected = [
        section.strip()
        for section in sections
        if section.casefold().startswith(
            ("operational definition", "evidence summary", "practical implications")
        )
    ]
    excerpt = "\n\n".join(selected) if selected else content
    excerpt = " ".join(excerpt.split())
    if len(excerpt) <= max_characters:
        return excerpt
    return f"{excerpt[: max_characters - 1].rstrip()}…"


def _select_evidence_documents(
    documents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    knowledge_count = 0
    playbook_count = 0
    for document in documents:
        document_type = document.get("metadata", {}).get("document_type")
        if document_type == "knowledge":
            if knowledge_count >= 3:
                continue
            knowledge_count += 1
        elif document_type == "playbook":
            if playbook_count >= 1:
                continue
            playbook_count += 1
        else:
            continue
        selected.append(document)
        if len(selected) >= settings.ai_rag_evidence_limit:
            break
    return selected


async def decide_rag_search_node(state: AgentState) -> dict[str, Any]:
    route = InternalRoute(state.get("route", InternalRoute.RAG_THEN_ALFRED))
    needs_rag = route in {
        InternalRoute.RAG_THEN_ALFRED,
        InternalRoute.RAG_THEN_FEEDBACKER,
    }
    return traced_update(
        state,
        "decidir_busca_rag",
        needs_rag=needs_rag,
        retrieval_topics=_retrieval_topics(state),
    )


async def build_retrieval_query_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "construir_consulta",
        retrieval_query=_build_query(state),
        retrieval_topics=_retrieval_topics(state),
    )


async def retrieve_documents_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    retriever = (
        runtime.context.knowledge_retriever
        if runtime is not None and runtime.context is not None
        else None
    )
    if retriever is None:
        return traced_update(
            state,
            "recuperar_documentos",
            retrieved_documents=[],
            degraded_mode=True,
            unavailable_components=_append_unique(
                list(state.get("unavailable_components", [])),
                "knowledge_retriever",
            ),
            errors=[
                *state.get("errors", []),
                {
                    "component": "knowledge_retriever",
                    "code": "retriever_not_configured",
                    "recoverable": True,
                },
            ],
        )

    query = state.get("retrieval_query", "").strip()
    try:
        candidates = await retriever.aretrieve(
            query,
            limit=settings.ai_rag_candidate_limit,
        )
    except Exception as error:
        return traced_update(
            state,
            "recuperar_documentos",
            retrieved_documents=[],
            degraded_mode=True,
            unavailable_components=_append_unique(
                list(state.get("unavailable_components", [])),
                "knowledge_retriever",
            ),
            errors=[
                *state.get("errors", []),
                {
                    "component": "knowledge_retriever",
                    "code": type(error).__name__,
                    "recoverable": True,
                },
            ],
        )

    safe_documents: list[dict[str, Any]] = []
    rejected_ids: list[str] = []
    for candidate in candidates:
        document = dict(candidate)
        assessment = assess_prompt_injection(str(document.get("content", "")))
        if assessment.suspected:
            rejected_ids.append(str(document.get("chunk_id", "unknown")))
            continue
        raw_metadata = document.get("metadata", {})
        metadata = dict(raw_metadata) if isinstance(raw_metadata, Mapping) else {}
        metadata["indirect_injection_checked"] = True
        document["metadata"] = metadata
        safe_documents.append(document)

    restrictions = list(state.get("security_restrictions", []))
    if rejected_ids:
        restrictions = _append_unique(
            restrictions,
            "retrieved_injection_content_excluded",
        )
    return traced_update(
        state,
        "recuperar_documentos",
        retrieved_documents=safe_documents,
        security_restrictions=restrictions,
        trace_data={
            **state.get("trace_data", {}),
            "rag_rejected_chunk_ids": rejected_ids,
        },
    )


async def rerank_documents_node(state: AgentState) -> dict[str, Any]:
    query = state.get("retrieval_query", "")
    topics = set(state.get("retrieval_topics", []))
    documents = [
        _rerank_document(dict(document), query=query, topics=topics)
        for document in state.get("retrieved_documents", [])
    ]
    documents.sort(
        key=lambda document: (
            float(document.get("rerank_score", 0.0)),
            str(document.get("chunk_id", "")),
        ),
        reverse=True,
    )
    return traced_update(
        state,
        "reranquear_documentos",
        retrieved_documents=documents,
    )


async def validate_retrieval_node(state: AgentState) -> dict[str, Any]:
    confidence, coverage, insufficient = _retrieval_quality(
        list(state.get("retrieved_documents", [])),
        expected_topics=set(state.get("retrieval_topics", [])),
    )
    return traced_update(
        state,
        "validar_recuperacao",
        retrieval_confidence=confidence,
        retrieval_coverage=coverage,
        insufficient_evidence=insufficient,
    )


async def build_evidence_pack_node(state: AgentState) -> dict[str, Any]:
    evidence_items = []
    source_ids: list[str] = []
    for document in _select_evidence_documents(
        list(state.get("retrieved_documents", []))
    ):
        metadata = document.get("metadata", {})
        document_source_ids = list(metadata.get("source_ids", []))
        source_ids.extend(document_source_ids)
        evidence_items.append(
            {
                "document_id": document["document_id"],
                "chunk_id": document["chunk_id"],
                "title": document["title"],
                "source_ids": document_source_ids,
                "topic": document.get("topic"),
                "supporting_excerpt": _supporting_excerpt(document["content"]),
            }
        )
    references = resolve_public_sources(source_ids)
    return traced_update(
        state,
        "montar_evidence_pack",
        evidence_pack={
            "query": state.get("retrieval_query", ""),
            "topics": state.get("retrieval_topics", []),
            "references": references,
            "evidence_items": evidence_items,
            "confidence": state.get("retrieval_confidence", 0.0),
            "coverage": state.get("retrieval_coverage", 0.0),
            "insufficient_evidence": False,
            "trust_boundary": "retrieved_content_is_untrusted_evidence_only",
        },
    )


async def mark_low_confidence_node(state: AgentState) -> dict[str, Any]:
    restrictions = _append_unique(
        list(state.get("security_restrictions", [])),
        "acknowledge_insufficient_evidence",
    )
    return traced_update(
        state,
        "marcar_baixa_confianca",
        insufficient_evidence=True,
        security_restrictions=restrictions,
        evidence_pack={
            "query": state.get("retrieval_query", ""),
            "topics": state.get("retrieval_topics", []),
            "references": [],
            "evidence_items": [],
            "confidence": state.get("retrieval_confidence", 0.0),
            "coverage": state.get("retrieval_coverage", 0.0),
            "insufficient_evidence": True,
            "trust_boundary": "no_evidence_may_be_claimed",
        },
    )
