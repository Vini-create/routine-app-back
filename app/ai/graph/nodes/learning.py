"""Asynchronous, deterministic intervention follow-up nodes."""

from datetime import timedelta
from typing import Any
from uuid import UUID

from langgraph.runtime import Runtime
from sqlalchemy import select

from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.models.ai import AIIntervention


def _context(
    runtime: Runtime[GraphRuntimeContext] | None,
) -> GraphRuntimeContext | None:
    return runtime.context if runtime is not None else None


async def register_intervention_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    context = _context(runtime)
    metrics = list(state.get("success_metrics", []))
    if context is None or context.session is None or not metrics:
        return traced_update(state, "registrar_intervencao")
    user_id = context.require_user_id(state["user_id"])
    request_id = UUID(state["request_id"])
    existing = await context.session.scalar(
        select(AIIntervention).where(AIIntervention.request_id == request_id)
    )
    if existing is None:
        days = max(
            int(metric.get("evaluation_window_days", 14)) for metric in metrics
        )
        existing = AIIntervention(
            user_id=user_id,
            request_id=request_id,
            intervention_type="alfred_recommendation",
            before_metrics=state.get("habit_metrics", {}).get("summary", {}),
            expected_metrics=metrics,
            evaluation_due_at=context.current_time() + timedelta(days=days),
        )
        context.session.add(existing)
        await context.session.flush()
    return traced_update(
        state,
        "registrar_intervencao",
        trace_data={
            **state.get("trace_data", {}),
            "intervention_id": str(existing.id),
        },
    )


async def observe_outcome_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    context = _context(runtime)
    if context is None or context.session is None:
        return traced_update(state, "observar_resultado")
    user_id = context.require_user_id(state["user_id"])
    intervention = await context.session.scalar(
        select(AIIntervention).where(
            AIIntervention.request_id == UUID(state["request_id"]),
            AIIntervention.user_id == user_id,
        )
    )
    if intervention is not None:
        intervention.after_metrics = state.get("habit_metrics", {}).get(
            "summary", {}
        )
        context.session.add(intervention)
        await context.session.flush()
    return traced_update(state, "observar_resultado")


async def evaluate_effectiveness_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    context = _context(runtime)
    outcome = "not_evaluated"
    if context is not None and context.session is not None:
        user_id = context.require_user_id(state["user_id"])
        intervention = await context.session.scalar(
            select(AIIntervention).where(
                AIIntervention.request_id == UUID(state["request_id"]),
                AIIntervention.user_id == user_id,
            )
        )
        if intervention is not None and intervention.after_metrics is not None:
            before = float(
                intervention.before_metrics.get("completion_rate") or 0
            )
            after = float(intervention.after_metrics.get("completion_rate") or 0)
            delta = after - before
            outcome = (
                "improved"
                if delta >= 0.05
                else "declined"
                if delta <= -0.05
                else "stable"
            )
            intervention.outcome = outcome
            intervention.evaluated_at = context.current_time()
            context.session.add(intervention)
            await context.session.flush()
    return traced_update(
        state,
        "avaliar_eficacia",
        trace_data={**state.get("trace_data", {}), "intervention_outcome": outcome},
    )
