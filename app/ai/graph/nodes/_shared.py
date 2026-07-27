"""Small deterministic helpers shared by graph nodes."""

from collections.abc import Mapping
from typing import Any

from app.ai.graph.state import AgentState


def traced_update(
    state: AgentState,
    node_name: str,
    /,
    **changes: Any,
) -> dict[str, Any]:
    """Return a node delta and append deterministic trace information.

    The zero latency is intentional in the skeleton. Real integrations will
    replace it with measured durations while preserving the same state shape.
    """

    supplied_trace_data = changes.pop("trace_data", None)
    trace_data = dict(state.get("trace_data", {}))
    if supplied_trace_data is not None:
        trace_data.update(dict(supplied_trace_data))
    visited_nodes = list(trace_data.get("visited_nodes", []))
    visited_nodes.append(node_name)
    trace_data["visited_nodes"] = visited_nodes

    latency_metrics = dict(state.get("latency_metrics", {}))
    latency_metrics[node_name] = 0.0

    return {
        **changes,
        "trace_data": trace_data,
        "latency_metrics": latency_metrics,
    }


def merged_mapping(
    current: Mapping[str, Any] | None,
    /,
    **changes: Any,
) -> dict[str, Any]:
    """Copy a mapping before changing it so state values are never mutated."""

    return {**dict(current or {}), **changes}
