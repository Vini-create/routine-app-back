"""Output criticism plus schema and patch preflight validation."""

from typing import Any
from uuid import UUID

from langgraph.runtime import Runtime
from pydantic import ValidationError

from app.ai.domain.enums import InternalRoute
from app.ai.domain.errors import AIApplicationError
from app.ai.graph.nodes._model import model_failure_update, model_usage_update
from app.ai.graph.nodes._shared import merged_mapping, traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.models.gateway import ModelRole
from app.ai.prompts.critic import build_critic_system_prompt
from app.ai.prompts.payloads import bounded_json
from app.ai.schemas.analysis import AnalysisReport
from app.ai.schemas.critic import CriticReview
from app.ai.schemas.patches import ProposedPatch
from app.ai.services.patch_service import (
    persist_pending_patch,
    validate_and_simulate_patch,
)


async def decide_critic_use_node(state: AgentState) -> dict[str, Any]:
    route = state.get("route")
    required = route in {
        InternalRoute.FEEDBACKER,
        InternalRoute.RAG_THEN_FEEDBACKER,
    } or state.get("proposed_patch") is not None
    return traced_update(
        state,
        "decidir_uso_critico",
        critic_required=state.get("critic_required", required),
        revision_count=state.get("revision_count", 0),
    )


async def critique_output_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    if state.get("revision_count", 0) > 0:
        return traced_update(
            state,
            "criticar_saida",
            critic_output={
                **state.get("critic_output", {}),
                "approved": True,
                "post_revision_validation": "bounded_revision_applied",
            },
        )

    gateway = (
        runtime.context.model_gateway
        if runtime is not None and runtime.context is not None
        else None
    )
    if gateway is None:
        current = dict(state.get("critic_output", {}))
        return traced_update(
            state,
            "criticar_saida",
            critic_output={
                "approved": bool(current.get("approved", True)),
                "issues": list(current.get("issues", [])),
                "revised_message": current.get("revised_message"),
            },
        )
    try:
        result = await gateway.invoke_structured(
            role=ModelRole.CRITIC,
            schema=CriticReview,
            system_prompt=build_critic_system_prompt(
                state.get("response_language", "en")
            ),
            user_prompt=bounded_json(
                {
                    "USER_INPUT": state["original_input"],
                    "draft_message": state.get("rendered_response", ""),
                    "analysis": state.get("analysis_report"),
                    "proposed_patch": state.get("proposed_patch"),
                    "evidence_items": state.get("evidence_pack", {}).get(
                        "evidence_items", []
                    ),
                    "safety": {
                        "level": state.get("safety_level"),
                        "restrictions": state.get("security_restrictions", []),
                    },
                },
                max_chars=18_000,
            ),
        )
        return traced_update(
            state,
            "criticar_saida",
            critic_output=result.parsed.model_dump(mode="json"),
            token_usage=model_usage_update(state, result, ModelRole.CRITIC),
        )
    except AIApplicationError as error:
        # A critic outage must not invent a rewrite. The already schema-bounded
        # main response remains available and degradation is explicit.
        return traced_update(
            state,
            "criticar_saida",
            critic_output={"approved": True, "issues": ["critic_unavailable"]},
            **model_failure_update(
                state,
                error,
                component="critic_model",
                fallback="schema_validated_draft",
            ),
        )


async def revise_output_node(state: AgentState) -> dict[str, Any]:
    revised = state.get("critic_output", {}).get("revised_message")
    return traced_update(
        state,
        "revisar_saida",
        revision_count=state.get("revision_count", 0) + 1,
        rendered_response=(
            str(revised) if revised else state.get("rendered_response", "")
        ),
    )


async def validate_schema_node(state: AgentState) -> dict[str, Any]:
    errors: list[str] = []
    try:
        if state.get("analysis_report") is not None:
            AnalysisReport.model_validate(state["analysis_report"])
        if state.get("proposed_patch") is not None:
            ProposedPatch.model_validate(state["proposed_patch"])
        message = state.get("rendered_response")
        if not message or len(message) > 12_000:
            errors.append("rendered_response_length")
    except ValidationError as exc:
        errors.append(f"schema:{exc.title}")
    return traced_update(
        state,
        "validar_schema",
        schema_valid=not errors,
        validation_errors=errors,
    )


async def validate_patch_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    validation = dict(state.get("patch_validation", {}))
    try:
        patch = ProposedPatch.model_validate(state.get("proposed_patch"))
        valid = patch.entity_id is not None
        errors = [] if valid else ["entity_id_required"]
        graph_context = (
            runtime.context
            if runtime is not None and runtime.context is not None
            else None
        )
        if valid and graph_context is not None and graph_context.session is not None:
            user_id = graph_context.require_user_id(state["user_id"])
            simulation = await validate_and_simulate_patch(
                graph_context.session,
                user_id=user_id,
                patch=patch,
            )
            simulation_data = simulation.public()
        else:
            simulation_data = state.get("patch_simulation", {})
    except AIApplicationError as exc:
        valid = False
        errors = [exc.code.value]
        simulation_data = {}
    except ValidationError as exc:
        valid = False
        errors = [f"schema:{exc.title}"]
        simulation_data = {}
    validation.setdefault("valid", valid)
    validation.setdefault("safe", validation["valid"])
    validation.setdefault("errors", errors)
    return traced_update(
        state,
        "validar_patch",
        patch_validation=validation,
        patch_simulation=simulation_data,
    )


async def simulate_patch_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "simular_patch",
        patch_simulation=state.get(
            "patch_simulation",
            {
                "status": "not_available",
                "before": {},
                "after": {},
            },
        ),
    )


async def convert_patch_to_text_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "converter_patch_em_texto",
        proposed_patch=None,
        patch_requires_confirmation=False,
        rendered_response=state.get(
            "rendered_response",
            "A alteração não é segura para aplicação automática.",
        ),
    )


async def prepare_confirmation_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    validation = merged_mapping(
        state.get("patch_validation"),
        confirmation_prepared=True,
    )
    graph_context = (
        runtime.context
        if runtime is not None and runtime.context is not None
        else None
    )
    persisted_patch_id = state.get("patch_id")
    public_patch = state.get("proposed_patch")
    if (
        persisted_patch_id is None
        and public_patch is not None
        and graph_context is not None
        and graph_context.session is not None
        and state.get("conversation_id") is not None
    ):
        user_id = graph_context.require_user_id(state["user_id"])
        patch = ProposedPatch.model_validate(public_patch)
        simulation = await validate_and_simulate_patch(
            graph_context.session,
            user_id=user_id,
            patch=patch,
        )
        persisted = await persist_pending_patch(
            graph_context.session,
            request_id=UUID(state["request_id"]),
            user_id=user_id,
            conversation_id=UUID(state["conversation_id"]),
            patch=patch,
            simulation=simulation,
            now=graph_context.current_time(),
        )
        persisted_patch_id = str(persisted.id)
        public_patch = patch.model_copy(
            update={
                "patch_id": persisted.id,
                "simulation": simulation.public(),
            }
        ).model_dump(mode="json")
    return traced_update(
        state,
        "preparar_confirmacao",
        patch_validation=validation,
        patch_requires_confirmation=True,
        patch_id=persisted_patch_id,
        proposed_patch=public_patch,
    )
