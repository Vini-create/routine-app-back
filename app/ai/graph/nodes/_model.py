"""Shared model-call accounting and fail-closed degradation helpers."""

from typing import Any

from app.ai.domain.errors import AIApplicationError
from app.ai.graph.state import AgentState
from app.ai.models.gateway import ModelInvocationResult, ModelRole


def model_usage_update(
    state: AgentState,
    result: ModelInvocationResult[Any],
    role: ModelRole,
) -> dict[str, Any]:
    current = dict(state.get("token_usage", {}))
    by_role = dict(current.get("by_role", {}))
    role_usage = dict(by_role.get(role.value, {}))
    for field in ("input_tokens", "output_tokens", "total_tokens"):
        amount = int(result.usage.get(field, 0))
        current[field] = int(current.get(field, 0)) + amount
        role_usage[field] = int(role_usage.get(field, 0)) + amount
    current["model_calls"] = int(current.get("model_calls", 0)) + 1
    role_usage["calls"] = int(role_usage.get("calls", 0)) + 1
    role_usage["model"] = result.model
    by_role[role.value] = role_usage
    current["by_role"] = by_role
    return current


def model_failure_update(
    state: AgentState,
    error: AIApplicationError,
    *,
    component: str,
    fallback: str,
) -> dict[str, Any]:
    errors = list(state.get("errors", []))
    errors.append(
        {
            "code": error.code.value,
            "message": error.message,
            "component": component,
        }
    )
    unavailable = list(state.get("unavailable_components", []))
    if component not in unavailable:
        unavailable.append(component)
    return {
        "degraded_mode": True,
        "errors": errors,
        "unavailable_components": unavailable,
        "fallback_used": fallback,
    }
