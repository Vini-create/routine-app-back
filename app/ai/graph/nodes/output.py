"""Final response and trace nodes."""

from typing import Any

from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.state import AgentState
from app.ai.services.language_service import resolve_response_language


def _response_message(state: AgentState) -> str:
    safe_response = state.get("safe_response", {})
    if safe_response:
        return str(safe_response.get("message", "Resposta segura."))
    return state.get("rendered_response", "Resposta do Alfred de teste.")


async def format_response_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "formatar_resposta",
        final_response={
            "request_id": state["request_id"],
            "conversation_id": state["conversation_id"],
            "route": (state["route"].value if state.get("route") is not None else None),
            "message": _response_message(state),
            "references": state.get("evidence_pack", {}).get("references", []),
            "analysis": state.get("analysis_report"),
            "proposed_patch": state.get("proposed_patch"),
            "requires_confirmation": state.get(
                "patch_requires_confirmation",
                False,
            ),
        },
    )


async def translate_response_node(state: AgentState) -> dict[str, Any]:
    """Finalize localization without making a translation-model call."""

    final_response = dict(state.get("final_response", {}))
    if not final_response:
        final_response = {
            "request_id": state["request_id"],
            "conversation_id": state["conversation_id"],
            "route": (state["route"].value if state.get("route") is not None else None),
            "message": _response_message(state),
            "references": [],
            "analysis": None,
            "proposed_patch": None,
            "requires_confirmation": False,
        }
    response_language = resolve_response_language(
        state.get("response_language", state.get("detected_language")),
        state.get("profile", {}).get("language"),
    )
    final_response["language"] = response_language
    final_response["translation_applied"] = False
    return traced_update(
        state,
        "traduzir_resposta",
        response_language=response_language,
        final_response=final_response,
    )


async def finalize_trace_node(state: AgentState) -> dict[str, Any]:
    trace_data = dict(state.get("trace_data", {}))
    trace_data["status"] = "completed"
    update = traced_update(state, "finalizar_trace", trace_data=trace_data)
    update["trace_data"]["status"] = "completed"
    return update
