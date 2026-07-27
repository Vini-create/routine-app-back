"""Human-in-the-loop nodes backed by the transactional patch service."""

from typing import Any
from uuid import UUID

from langgraph.runtime import Runtime

from app.ai.graph.nodes._shared import merged_mapping, traced_update
from app.ai.graph.runtime import GraphRuntimeContext
from app.ai.graph.state import AgentState
from app.ai.schemas.patches import ProposedPatch
from app.ai.services.patch_service import (
    accept_patch,
    reject_patch,
    validate_and_simulate_patch,
)


async def await_confirmation_node(state: AgentState) -> dict[str, Any]:
    return traced_update(
        state,
        "aguardar_confirmacao",
        patch_requires_confirmation=True,
    )


async def apply_patch_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    graph_context = (
        runtime.context
        if runtime is not None and runtime.context is not None
        else None
    )
    if (
        graph_context is None
        or graph_context.session is None
        or state.get("patch_id") is None
    ):
        status = "application_requires_persisted_runtime"
        audit_id = None
    else:
        user_id = graph_context.require_user_id(state["user_id"])
        patch, audit = await accept_patch(
            graph_context.session,
            patch_id=UUID(state["patch_id"]),
            user_id=user_id,
            idempotency_key=UUID(
                state.get("idempotency_key") or state["request_id"]
            ),
            now=graph_context.current_time(),
        )
        status = patch.status
        audit_id = str(audit.id)
    return traced_update(
        state,
        "aplicar_patch",
        patch_validation=merged_mapping(
            state.get("patch_validation"),
            application_status=status,
            audit_id=audit_id,
        ),
    )


async def register_rejection_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    graph_context = (
        runtime.context
        if runtime is not None and runtime.context is not None
        else None
    )
    status = "rejected"
    audit_id = None
    if (
        graph_context is not None
        and graph_context.session is not None
        and state.get("patch_id") is not None
    ):
        user_id = graph_context.require_user_id(state["user_id"])
        patch, audit = await reject_patch(
            graph_context.session,
            patch_id=UUID(state["patch_id"]),
            user_id=user_id,
            reason="Rejected by the authenticated user.",
            now=graph_context.current_time(),
        )
        status = patch.status
        audit_id = str(audit.id)
    return traced_update(
        state,
        "registrar_rejeicao",
        patch_validation=merged_mapping(
            state.get("patch_validation"),
            application_status=status,
            audit_id=audit_id,
        ),
        patch_requires_confirmation=False,
    )


async def revalidate_edited_patch_node(
    state: AgentState,
    runtime: Runtime[GraphRuntimeContext] | None = None,
) -> dict[str, Any]:
    graph_context = (
        runtime.context
        if runtime is not None and runtime.context is not None
        else None
    )
    simulation = state.get("patch_simulation", {})
    if (
        graph_context is not None
        and graph_context.session is not None
        and state.get("proposed_patch") is not None
    ):
        user_id = graph_context.require_user_id(state["user_id"])
        simulation = (
            await validate_and_simulate_patch(
                graph_context.session,
                user_id=user_id,
                patch=ProposedPatch.model_validate(state["proposed_patch"]),
            )
        ).public()
    return traced_update(
        state,
        "revalidar_patch_editado",
        patch_validation=merged_mapping(
            state.get("patch_validation"),
            valid=True,
            safe=True,
            edited=True,
        ),
        patch_simulation=simulation,
        human_decision=None,
    )


async def create_audit_node(state: AgentState) -> dict[str, Any]:
    application_status = state.get("patch_validation", {}).get(
        "application_status"
    )
    return traced_update(
        state,
        "criar_auditoria",
        patch_validation=merged_mapping(
            state.get("patch_validation"),
            audit_status=(
                "persisted_transactionally"
                if application_status == "applied"
                else "not_created"
            ),
        ),
        patch_requires_confirmation=False,
    )
