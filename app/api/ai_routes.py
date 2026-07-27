"""Single public Alfred API; Feedbacker remains an internal graph route."""

import asyncio
import json
import re
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.errors import AIApplicationError
from app.ai.repositories.persistence_repository import (
    create_conversation,
    get_owned_conversation,
    list_conversation_messages,
    list_conversations,
)
from app.ai.schemas.patches import (
    PatchAcceptRequest,
    PatchEditRequest,
    PatchRejectRequest,
)
from app.ai.schemas.requests import AIInvokeRequest
from app.ai.schemas.responses import (
    AICapabilitiesResponse,
    AIConversationCreate,
    AIConversationDetail,
    AIConversationSummary,
    AIInvokeResponse,
    AIMessageResponse,
    AIUsageResponse,
    PatchResolutionResponse,
)
from app.ai.services.orchestrator import AIOrchestrator
from app.ai.services.patch_service import (
    accept_patch,
    edit_patch,
    public_patch,
    reject_patch,
)
from app.ai.services.usage_service import get_usage_snapshot
from app.api.dependencies import get_current_verified_user
from app.api.rate_limit import limiter
from app.billing.service import BillingAccess, require_active_billing_access
from app.db.db import get_session
from app.models.auth import User
from app.models.ai import AIConversation

# Coarse per-IP abuse protection. Per-plan limits are enforced transactionally
# in usage_service, so this guard must stay above the highest paid-plan limit.
AI_INFERENCE_RATE_LIMIT = "90/minute"
AI_READ_RATE_LIMIT = "60/minute"
AI_WRITE_RATE_LIMIT = "20/minute"

# This is deliberately small: it makes each SSE frame observable by the browser
# without turning a concise Alfred answer into a long typewriter animation.
STREAM_WORD_DELAY_SECONDS = 0.018


async def get_current_ai_billing_access(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> BillingAccess:
    """Fail closed before every public AI endpoint."""
    return await require_active_billing_access(session, current_user.id)


ai_router = APIRouter(
    prefix="/api/v1/ai",
    tags=["alfred"],
    dependencies=[Depends(get_current_ai_billing_access)],
)


def _orchestrator(
    session: AsyncSession,
    user: User,
) -> AIOrchestrator:
    return AIOrchestrator(session=session, user=user)


def _require_patch_entitlement(access: BillingAccess) -> None:
    if not access.entitlements.patch_generation_enabled:
        from app.ai.domain.errors import AIErrorCode

        raise AIApplicationError(
            AIErrorCode.PLAN_UNAVAILABLE,
            "Patch confirmation is unavailable on the current plan.",
        )


def _conversation_summary(conversation: AIConversation) -> AIConversationSummary:
    return AIConversationSummary.model_validate(
        {
            "id": conversation.id,
            "title": conversation.title,
            "summary_en": conversation.summary_en,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
    )


@ai_router.post("/invoke", response_model=AIInvokeResponse)
@limiter.limit(AI_INFERENCE_RATE_LIMIT)
async def invoke_alfred(
    request: Request,
    payload: AIInvokeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> AIInvokeResponse:
    return await _orchestrator(session, current_user).invoke(payload)


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


def _stream_word_chunks(message: str) -> list[str]:
    """Keep the original whitespace while emitting one readable word per frame."""
    return re.findall(r"\S+\s*", message)


@ai_router.post("/stream")
@limiter.limit(AI_INFERENCE_RATE_LIMIT)
async def stream_alfred(
    request: Request,
    payload: AIInvokeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        yield _sse(
            "status",
            {"node": "iniciar_estado", "message": "Alfred iniciou a solicitação."},
        )
        try:
            response = await _orchestrator(session, current_user).invoke(
                payload, is_stream=True
            )
            for reference in response.references:
                yield _sse("reference", reference.model_dump(mode="json"))
            if response.analysis is not None:
                yield _sse("analysis", response.analysis.model_dump(mode="json"))
            if response.proposed_patch is not None:
                yield _sse(
                    "patch",
                    {
                        "patch": response.proposed_patch.model_dump(mode="json"),
                        "requires_confirmation": True,
                    },
                )
            # The graph must finish before its structured artifacts can be
            # validated and persisted.  Once it has, emit one word at a time
            # and yield to the event loop between frames: without that await,
            # proxies and browsers commonly coalesce every token into one
            # response and the frontend cannot render incrementally.
            for word in _stream_word_chunks(response.message):
                yield _sse("token", {"content": word})
                await asyncio.sleep(STREAM_WORD_DELAY_SECONDS)
            yield _sse(
                "done",
                {
                    "request_id": response.request_id,
                    "conversation_id": response.conversation_id,
                    "route": response.route.value,
                    "usage": response.usage.model_dump(mode="json"),
                },
            )
        except AIApplicationError as error:
            yield _sse(
                "error",
                {
                    "request_id": error.request_id,
                    "code": error.code.value,
                    "message": error.message,
                },
            )

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@ai_router.get("/usage", response_model=AIUsageResponse)
@limiter.limit(AI_READ_RATE_LIMIT)
async def get_ai_usage(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> AIUsageResponse:
    snapshot = await get_usage_snapshot(
        session,
        user_id=current_user.id,
        timezone_name=current_user.timezone,
    )
    return AIUsageResponse.model_validate(snapshot, from_attributes=True)


@ai_router.get("/capabilities", response_model=AICapabilitiesResponse)
@limiter.limit(AI_READ_RATE_LIMIT)
async def get_ai_capabilities(
    request: Request,
    billing_access: BillingAccess = Depends(get_current_ai_billing_access),
) -> AICapabilitiesResponse:
    entitlements = billing_access.entitlements
    return AICapabilitiesResponse(
        plan=billing_access.plan_code.value,
        capabilities={
            "conversation": True,
            "deep_analysis": True,
            "rag": entitlements.rag_enabled,
            "patch_generation": entitlements.patch_generation_enabled,
            "memory": entitlements.memory_level,
            "streaming": True,
        },
    )


@ai_router.post(
    "/patches/{patch_id}/accept",
    response_model=PatchResolutionResponse,
)
@limiter.limit(AI_WRITE_RATE_LIMIT)
async def accept_ai_patch(
    request: Request,
    patch_id: UUID,
    payload: PatchAcceptRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    billing_access: BillingAccess = Depends(get_current_ai_billing_access),
) -> PatchResolutionResponse:
    _require_patch_entitlement(billing_access)
    patch, audit = await accept_patch(
        session,
        patch_id=patch_id,
        user_id=current_user.id,
        idempotency_key=payload.idempotency_key,
    )
    return PatchResolutionResponse.model_validate(
        {
            "patch_id": patch.id,
            "status": patch.status,
            "proposed_patch": public_patch(patch),
            "audit_id": audit.id,
            "requires_confirmation": False,
        }
    )


@ai_router.post(
    "/patches/{patch_id}/reject",
    response_model=PatchResolutionResponse,
)
@limiter.limit(AI_WRITE_RATE_LIMIT)
async def reject_ai_patch(
    request: Request,
    patch_id: UUID,
    payload: PatchRejectRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    billing_access: BillingAccess = Depends(get_current_ai_billing_access),
) -> PatchResolutionResponse:
    _require_patch_entitlement(billing_access)
    patch, audit = await reject_patch(
        session,
        patch_id=patch_id,
        user_id=current_user.id,
        reason=payload.reason,
    )
    return PatchResolutionResponse.model_validate(
        {
            "patch_id": patch.id,
            "status": patch.status,
            "proposed_patch": public_patch(patch),
            "audit_id": audit.id,
            "requires_confirmation": False,
        }
    )


@ai_router.post(
    "/patches/{patch_id}/edit",
    response_model=PatchResolutionResponse,
)
@limiter.limit(AI_WRITE_RATE_LIMIT)
async def edit_ai_patch(
    request: Request,
    patch_id: UUID,
    payload: PatchEditRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    billing_access: BillingAccess = Depends(get_current_ai_billing_access),
) -> PatchResolutionResponse:
    _require_patch_entitlement(billing_access)
    patch = await edit_patch(
        session,
        patch_id=patch_id,
        user_id=current_user.id,
        idempotency_key=payload.idempotency_key,
        operations=payload.operations,
    )
    return PatchResolutionResponse.model_validate(
        {
            "patch_id": patch.id,
            "status": patch.status,
            "proposed_patch": public_patch(patch),
            "requires_confirmation": True,
        }
    )


@ai_router.post(
    "/conversations",
    response_model=AIConversationSummary,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(AI_WRITE_RATE_LIMIT)
async def create_ai_conversation(
    request: Request,
    payload: AIConversationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> AIConversationSummary:
    conversation = await create_conversation(
        session,
        user_id=current_user.id,
        title_source=payload.title,
    )
    await session.commit()
    await session.refresh(conversation)
    return _conversation_summary(conversation)


@ai_router.get("/conversations", response_model=list[AIConversationSummary])
@limiter.limit(AI_READ_RATE_LIMIT)
async def list_ai_conversations(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> list[AIConversationSummary]:
    conversations = await list_conversations(session, user_id=current_user.id)
    return [_conversation_summary(item) for item in conversations]


@ai_router.get(
    "/conversations/{conversation_id}",
    response_model=AIConversationDetail,
)
@limiter.limit(AI_READ_RATE_LIMIT)
async def get_ai_conversation(
    request: Request,
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> AIConversationDetail:
    conversation = await get_owned_conversation(
        session,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    messages = await list_conversation_messages(
        session,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    summary = _conversation_summary(conversation)
    return AIConversationDetail(
        **summary.model_dump(),
        messages=[
            AIMessageResponse.model_validate(
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "route": message.route,
                    "analysis": message.analysis,
                    "references": message.references,
                    "proposed_patch": message.proposed_patch,
                    "requires_confirmation": message.requires_confirmation,
                    "patch_status": message.patch_status,
                    "request_id": message.request_id,
                    "created_at": message.created_at,
                }
            )
            for message in messages
        ],
    )


@ai_router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit(AI_WRITE_RATE_LIMIT)
async def delete_ai_conversation(
    request: Request,
    conversation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
) -> Response:
    conversation = await get_owned_conversation(
        session,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    from datetime import datetime, timezone

    conversation.deleted_at = datetime.now(timezone.utc)
    session.add(conversation)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
