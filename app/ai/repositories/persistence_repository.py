"""Owned, bounded persistence operations for Alfred."""

import hashlib
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.limits import MAX_ROLLING_SUMMARY_CHARS
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.models.ai import (
    AIConversation,
    AIFeedbackerDecisionMemory,
    AIGraphCheckpoint,
    AIMemory,
    AIMessage,
    AIProposedPatch,
)
from app.models.auth import User

MAX_CONVERSATION_MESSAGES = 100
MAX_CONVERSATIONS = 50
MAX_MEMORIES = 20
MAX_FEEDBACKER_DECISION_MEMORIES = 4


async def get_owned_conversation(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    user_id: UUID,
    include_deleted: bool = False,
) -> AIConversation:
    conversation = await session.get(AIConversation, conversation_id)
    if conversation is None:
        raise AIApplicationError(
            AIErrorCode.CONVERSATION_NOT_FOUND,
            "The Alfred conversation was not found.",
        )
    if conversation.user_id != user_id:
        raise AIApplicationError(
            AIErrorCode.CONVERSATION_FORBIDDEN,
            "The Alfred conversation belongs to another user.",
        )
    if conversation.deleted_at is not None and not include_deleted:
        raise AIApplicationError(
            AIErrorCode.CONVERSATION_NOT_FOUND,
            "The Alfred conversation was not found.",
        )
    return conversation


async def create_conversation(
    session: AsyncSession,
    *,
    user_id: UUID,
    title_source: str,
) -> AIConversation:
    title = " ".join(title_source.strip().split())[:160] or "Nova conversa"
    conversation = AIConversation(user_id=user_id, title=title)
    session.add(conversation)
    await session.flush()
    return conversation


async def resolve_conversation(
    session: AsyncSession,
    *,
    user_id: UUID,
    conversation_id: UUID | None,
    title_source: str,
) -> AIConversation:
    if conversation_id is None:
        return await create_conversation(
            session, user_id=user_id, title_source=title_source
        )
    return await get_owned_conversation(
        session, conversation_id=conversation_id, user_id=user_id
    )


async def list_conversations(
    session: AsyncSession,
    *,
    user_id: UUID,
) -> list[AIConversation]:
    result = await session.execute(
        select(AIConversation)
        .where(
            AIConversation.user_id == user_id,
            AIConversation.deleted_at.is_(None),
        )
        .order_by(AIConversation.updated_at.desc())
        .limit(MAX_CONVERSATIONS)
    )
    return list(result.scalars())


async def list_conversation_messages(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    user_id: UUID,
) -> list[AIMessage]:
    await get_owned_conversation(
        session, conversation_id=conversation_id, user_id=user_id
    )
    result = await session.execute(
        select(AIMessage)
        .where(
            AIMessage.conversation_id == conversation_id,
            AIMessage.user_id == user_id,
        )
        .order_by(AIMessage.created_at.desc())
        .limit(MAX_CONVERSATION_MESSAGES)
    )
    return list(reversed(list(result.scalars())))


async def find_checkpoint_replay(
    session: AsyncSession,
    *,
    user_id: UUID,
    request_id: UUID | None = None,
    idempotency_key: UUID | None = None,
) -> AIGraphCheckpoint | None:
    conditions = []
    if request_id is not None:
        conditions.append(AIGraphCheckpoint.request_id == request_id)
    if idempotency_key is not None:
        conditions.append(AIGraphCheckpoint.idempotency_key == idempotency_key)
    if not conditions:
        return None
    result = await session.execute(
        select(AIGraphCheckpoint).where(
            AIGraphCheckpoint.user_id == user_id,
            or_(*conditions),
        )
    )
    return result.scalar_one_or_none()


async def save_message(
    session: AsyncSession,
    *,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    request_id: UUID,
    route: str | None = None,
    detected_language: str | None = None,
    analysis: dict | None = None,
    references: list[dict] | None = None,
    proposed_patch: dict | None = None,
    requires_confirmation: bool | None = None,
    patch_status: str | None = None,
) -> AIMessage:
    message = AIMessage(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        request_id=request_id,
        route=route,
        detected_language=detected_language,
        analysis=analysis,
        references=references,
        proposed_patch=proposed_patch,
        requires_confirmation=requires_confirmation,
        patch_status=patch_status,
    )
    session.add(message)
    await session.flush()
    return message


async def load_relevant_memories(
    session: AsyncSession,
    *,
    user_id: UUID,
    now: datetime,
) -> list[dict]:
    result = await session.execute(
        select(AIMemory)
        .where(
            AIMemory.user_id == user_id,
            or_(AIMemory.expires_at.is_(None), AIMemory.expires_at > now),
        )
        .order_by(AIMemory.importance.desc(), AIMemory.updated_at.desc())
        .limit(MAX_MEMORIES)
    )
    return [
        {
            "id": str(memory.id),
            "content": memory.content,
            "memory_type": memory.memory_type,
            "confidence": float(memory.confidence),
            "importance": float(memory.importance),
            "source_request_id": str(memory.source_request_id),
            "expires_at": (
                memory.expires_at.isoformat() if memory.expires_at else None
            ),
        }
        for memory in result.scalars()
    ]


async def load_feedbacker_decision_memories(
    session: AsyncSession,
    *,
    user_id: UUID,
) -> list[dict]:
    """Return only the four newest human decisions for Feedbacker context."""

    result = await session.execute(
        select(AIFeedbackerDecisionMemory)
        .where(AIFeedbackerDecisionMemory.user_id == user_id)
        .order_by(
            AIFeedbackerDecisionMemory.created_at.desc(),
            AIFeedbackerDecisionMemory.id.desc(),
        )
        .limit(MAX_FEEDBACKER_DECISION_MEMORIES)
    )
    return [
        {
            "type": memory.adjustment_type,
            "context": memory.context,
            "decision": memory.decision,
            "reason": memory.reason,
            "inferred_preference": memory.inferred_preference,
            "confidence": float(memory.confidence),
            "created_at": memory.created_at.isoformat(),
        }
        for memory in result.scalars()
    ]


def _adjustment_type(patch: AIProposedPatch) -> str:
    fields = sorted(
        {
            str(operation.get("path", "")).removeprefix("/")
            for operation in patch.operations
            if operation.get("path")
        }
    )
    suffix = ",".join(fields) or "general"
    return f"{patch.entity_type}:{suffix}"[:160]


async def record_feedbacker_decision_memory(
    session: AsyncSession,
    *,
    patch: AIProposedPatch,
    decision: str,
    reason: str | None,
    created_at: datetime,
) -> AIFeedbackerDecisionMemory:
    """Persist a patch decision and atomically prune older user memories."""

    if decision not in {"accepted", "rejected"}:
        raise ValueError("decision must be accepted or rejected")

    # Patch resolutions for one user may arrive concurrently. Locking the owner
    # row serializes the insert-and-prune boundary and preserves the hard cap.
    await session.execute(
        select(User.id).where(User.id == patch.user_id).with_for_update()
    )

    normalized_reason = " ".join(reason.split())[:500] if reason else None
    if decision == "rejected":
        inferred_preference = (
            "Avoid repeating this adjustment in a similar context unless new "
            "evidence materially changes the recommendation."
        )
        if normalized_reason:
            inferred_preference += f" Consider the user's reason: {normalized_reason}"
        confidence = 0.85 if normalized_reason else 0.65
    else:
        inferred_preference = (
            "The user previously accepted this category of adjustment in a "
            "similar context; treat that as a preference signal, not a rule."
        )
        confidence = 0.65

    memory = AIFeedbackerDecisionMemory(
        user_id=patch.user_id,
        patch_id=patch.id,
        adjustment_type=_adjustment_type(patch),
        context=" ".join(patch.reason.split())[:1_000],
        decision=decision,
        reason=normalized_reason,
        inferred_preference=inferred_preference,
        confidence=Decimal(str(confidence)),
        created_at=created_at,
    )
    session.add(memory)
    await session.flush()

    stale_result = await session.execute(
        select(AIFeedbackerDecisionMemory.id)
        .where(AIFeedbackerDecisionMemory.user_id == patch.user_id)
        .order_by(
            AIFeedbackerDecisionMemory.created_at.desc(),
            AIFeedbackerDecisionMemory.id.desc(),
        )
        .offset(MAX_FEEDBACKER_DECISION_MEMORIES)
    )
    stale_ids = list(stale_result.scalars())
    if stale_ids:
        await session.execute(
            delete(AIFeedbackerDecisionMemory).where(
                AIFeedbackerDecisionMemory.id.in_(stale_ids)
            )
        )
    return memory


def normalize_conversation_summary(summary: str | None) -> str | None:
    """Normalize a model-generated rolling summary before persistence."""

    if summary is None:
        return None
    normalized = " ".join(summary.split())
    return normalized[:MAX_ROLLING_SUMMARY_CHARS] or None


def memory_fingerprint(content: str) -> str:
    canonical = " ".join(content.casefold().split())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def upsert_memory(
    session: AsyncSession,
    *,
    user_id: UUID,
    conversation_id: UUID | None,
    memory_type: str,
    content: str,
    confidence: float,
    importance: float,
    source_request_id: UUID,
    expires_at: datetime | None,
) -> AIMemory:
    fingerprint = memory_fingerprint(content)
    result = await session.execute(
        select(AIMemory).where(
            AIMemory.user_id == user_id,
            AIMemory.content_fingerprint == fingerprint,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        existing.confidence = Decimal(str(max(float(existing.confidence), confidence)))
        existing.importance = Decimal(str(max(float(existing.importance), importance)))
        existing.expires_at = expires_at or existing.expires_at
        existing.source_request_id = source_request_id
        session.add(existing)
        return existing

    memory = AIMemory(
        user_id=user_id,
        conversation_id=conversation_id,
        memory_type=memory_type,
        content=content,
        content_fingerprint=fingerprint,
        confidence=Decimal(str(confidence)),
        importance=Decimal(str(importance)),
        source_request_id=source_request_id,
        expires_at=expires_at,
    )
    session.add(memory)
    return memory
