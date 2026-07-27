"""Hybrid router: local rules first, model only for genuine ambiguity."""

from typing import Any

from langgraph.runtime import Runtime

from app.ai.domain.enums import (
    InternalRoute,
    SelectedSkill,
    capability_for_route,
)
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.graph.nodes._model import model_failure_update, model_usage_update
from app.ai.graph.nodes._shared import traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.models.gateway import ModelRole
from app.ai.prompts.payloads import bounded_json
from app.ai.prompts.routing import build_routing_system_prompt
from app.ai.schemas.routing import RoutingDecision
from app.ai.services.routing_service import classify_route


async def classify_intent_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    selected_skill = state["selected_skill"]
    normalized_skill = (
        selected_skill
        if isinstance(selected_skill, SelectedSkill)
        else SelectedSkill(selected_skill)
    )
    current_route = state.get("route")
    model_changes: dict[str, Any] = {}
    if current_route is not None:
        route = InternalRoute(current_route)
        detected_intent = state.get("detected_intent", "preselected_test_route")
        confidence = state.get("intent_confidence", 1.0)
        route_confidence = state.get("route_confidence", 1.0)
        reason = state.get("route_reason", "Route supplied by the trusted caller.")
        required_context = list(state.get("required_context", []))
    else:
        decision = classify_route(
            state.get("normalized_input", state["original_input"]),
            normalized_skill,
        )
        model_gateway = (
            runtime.context.model_gateway
            if runtime is not None and runtime.context is not None
            else None
        )
        if decision.needs_model and model_gateway is not None:
            try:
                result = await model_gateway.invoke_structured(
                    role=ModelRole.ROUTER,
                    schema=RoutingDecision,
                    system_prompt=build_routing_system_prompt(),
                    user_prompt=bounded_json(
                        {
                            "USER_INPUT": state["original_input"],
                            "selected_skill": normalized_skill.value,
                            "behavioral_summary": state.get(
                                "behavioral_state",
                                {},
                            ),
                        },
                        max_chars=8_000,
                    ),
                )
                parsed = result.parsed
                if parsed.route is InternalRoute.SAFE_RESPONSE:
                    raise AIApplicationError(
                        code=AIErrorCode.MODEL_INVALID_OUTPUT,
                        message="The routing model selected a forbidden route.",
                    )
                route = parsed.route
                detected_intent = parsed.detected_intent
                confidence = parsed.intent_confidence
                route_confidence = parsed.route_confidence
                reason = parsed.route_reason
                required_context = parsed.required_context
                model_changes["token_usage"] = model_usage_update(
                    state,
                    result,
                    ModelRole.ROUTER,
                )
            except AIApplicationError as error:
                route = decision.route
                detected_intent = decision.detected_intent
                confidence = decision.confidence
                route_confidence = decision.confidence
                reason = decision.reason
                required_context = []
                model_changes.update(
                    model_failure_update(
                        state,
                        error,
                        component="router_model",
                        fallback="deterministic_router_default",
                    )
                )
        else:
            route = decision.route
            detected_intent = decision.detected_intent
            confidence = decision.confidence
            route_confidence = decision.confidence
            reason = decision.reason
            required_context = (
                ["model_routing"]
                if decision.needs_model
                else list(state.get("required_context", []))
            )
    return traced_update(
        state,
        "classificar_intencao",
        detected_intent=detected_intent,
        intent_confidence=confidence,
        route=route,
        capability=capability_for_route(route),
        route_confidence=route_confidence,
        route_reason=reason,
        required_context=required_context,
        needs_rag=route
        in {
            InternalRoute.RAG_THEN_ALFRED,
            InternalRoute.RAG_THEN_FEEDBACKER,
        },
        rag_destination=(
            "feedbacker" if route is InternalRoute.RAG_THEN_FEEDBACKER else "alfred"
        ),
        **model_changes,
    )
