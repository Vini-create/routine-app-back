"""Deterministic behavioral-intelligence nodes kept outside the LLM."""

from datetime import datetime, timezone
from typing import Any

from langgraph.runtime import Runtime

from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.services.behavior_service import (
    calculate_behavior_metrics,
    detect_behavior_anomalies,
    detect_behavior_trends,
    predict_dropout_risk,
)


def _now(runtime: Runtime[GraphRuntimeContext] | None) -> datetime:
    if runtime is not None and runtime.context is not None:
        return runtime.context.current_time()
    return datetime.now(timezone.utc)


async def calculate_metrics_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    return traced_update(
        state,
        "calcular_metricas",
        habit_metrics=calculate_behavior_metrics(
            dict(state.get("user_context", {})),
            now=_now(runtime),
        ),
    )


async def detect_trends_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "detectar_tendencias",
        detected_trends=detect_behavior_trends(dict(state.get("habit_metrics", {}))),
    )


async def detect_anomalies_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "detectar_anomalias",
        detected_anomalies=detect_behavior_anomalies(
            dict(state.get("habit_metrics", {})),
            list(state.get("detected_trends", [])),
        ),
    )


async def predict_dropout_risk_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "prever_risco_abandono",
        dropout_risk=predict_dropout_risk(
            dict(state.get("habit_metrics", {})),
            list(state.get("detected_trends", [])),
            list(state.get("detected_anomalies", [])),
        ),
    )


async def build_behavioral_state_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "construir_estado_comportamental",
        behavioral_state={
            "metrics": state.get("habit_metrics", {}),
            "trends": state.get("detected_trends", []),
            "anomalies": state.get("detected_anomalies", []),
            "dropout_risk": state.get("dropout_risk", {}),
            "methodology": {
                "metrics": "scheduled_occurrences_and_logs",
                "trends": "two_14_day_windows",
                "anomalies": "transparent_threshold_rules",
                "risk": "transparent_rules_v1",
                "uses_llm": False,
            },
        },
    )
