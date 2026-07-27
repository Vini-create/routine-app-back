"""Bounded memory extraction, validation, deduplication and persistence."""

from datetime import timedelta
from typing import Any
from uuid import UUID

from langgraph.runtime import Runtime

from app.ai.graph.nodes.entry import assess_prompt_injection
from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.repositories.persistence_repository import (
    memory_fingerprint,
    upsert_memory,
)


async def decide_memory_node(state: AgentState) -> dict[str, Any]:
    return traced_update(state, "decidir_memoria")


async def extract_memory_node(state: AgentState) -> dict[str, Any]:
    safe_memories: list[dict[str, Any]] = []
    for candidate in state.get(
        "memories_to_store", state.get("memory_candidates", [])
    ):
        if not isinstance(candidate, dict):
            continue
        content = str(candidate.get("content", candidate.get("value", ""))).strip()
        confidence = float(candidate.get("confidence", 0.6))
        if (
            10 <= len(content) <= 500
            and confidence >= 0.6
            and not assess_prompt_injection(content).suspected
        ):
            safe_memories.append(
                {
                    "content": content,
                    "confidence": min(confidence, 1.0),
                    "importance": min(
                        max(float(candidate.get("importance", 0.5)), 0.0),
                        1.0,
                    ),
                    "source": str(candidate.get("source", "alfred")),
                }
            )
    return traced_update(
        state,
        "extrair_memoria",
        memories_to_store=safe_memories,
    )


async def classify_memory_node(state: AgentState) -> dict[str, Any]:
    memories = [
        {
            **memory,
            "memory_type": (
                "semantic"
                if any(
                    marker in memory["content"].casefold()
                    for marker in ("prefiro", "prefere", "i prefer", "mi preferencia")
                )
                else memory.get("memory_type", "short_term")
            ),
        }
        for memory in state.get("memories_to_store", [])
        if isinstance(memory, dict)
    ]
    return traced_update(
        state,
        "classificar_memoria",
        memories_to_store=memories,
    )


async def deduplicate_memory_node(state: AgentState) -> dict[str, Any]:
    unique_memories: list[dict[str, Any]] = []
    fingerprints: set[str] = set()
    for memory in state.get("memories_to_store", []):
        fingerprint = memory_fingerprint(str(memory.get("content", "")))
        if fingerprint not in fingerprints:
            fingerprints.add(fingerprint)
            unique_memories.append(memory)
    return traced_update(
        state,
        "deduplicar_memoria",
        memories_to_store=unique_memories,
    )


async def persist_memory_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    graph_context = (
        runtime.context
        if runtime is not None and runtime.context is not None
        else None
    )
    if graph_context is None or graph_context.session is None:
        return traced_update(
            state,
            "persistir_memoria",
            fallback_used=state.get("fallback_used", "memory_store_unavailable"),
        )

    user_id = graph_context.require_user_id(state["user_id"])
    request_id = UUID(state["request_id"])
    conversation_id = (
        UUID(state["conversation_id"]) if state.get("conversation_id") else None
    )
    current = graph_context.current_time()
    persisted = 0
    for memory in state.get("memories_to_store", [])[:5]:
        memory_type = str(memory.get("memory_type", "short_term"))
        expires_at = {
            "short_term": current + timedelta(days=30),
            "episodic": current + timedelta(days=90),
            "semantic": current + timedelta(days=180),
        }.get(memory_type, current + timedelta(days=30))
        await upsert_memory(
            graph_context.session,
            user_id=user_id,
            conversation_id=conversation_id,
            memory_type=memory_type,
            content=str(memory["content"]),
            confidence=float(memory["confidence"]),
            importance=float(memory["importance"]),
            source_request_id=request_id,
            expires_at=expires_at,
        )
        persisted += 1
    return traced_update(
        state,
        "persistir_memoria",
        trace_data={
            **state.get("trace_data", {}),
            "memories_persisted": persisted,
        },
    )
