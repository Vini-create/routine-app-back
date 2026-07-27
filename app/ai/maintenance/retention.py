"""Delete expired AI content while retaining observability for longer."""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.db import async_session_maker, engine
from app.models.ai import (
    AIConversation,
    AIFeedbackerDecisionMemory,
    AIGraphCheckpoint,
    AIIntervention,
    AIMemory,
    AIMessage,
    AIProposedPatch,
    AIUsageEvent,
    ChatMessage,
)


@dataclass(frozen=True, slots=True)
class AIRetentionPolicy:
    """Retention windows ordered by sensitivity and operational value."""

    message_days: int = 90
    patch_days: int = 90
    expired_patch_grace_days: int = 7
    deleted_conversation_days: int = 30
    intervention_days: int = 180
    observability_days: int = 400

    @classmethod
    def from_settings(cls) -> "AIRetentionPolicy":
        return cls(
            message_days=settings.ai_message_retention_days,
            patch_days=settings.ai_patch_retention_days,
            expired_patch_grace_days=settings.ai_expired_patch_grace_days,
            deleted_conversation_days=(
                settings.ai_deleted_conversation_retention_days
            ),
            intervention_days=settings.ai_intervention_retention_days,
            observability_days=settings.ai_observability_retention_days,
        )

    def __post_init__(self) -> None:
        values = asdict(self)
        if any(value <= 0 for value in values.values()):
            raise ValueError("retention windows must be positive")
        if self.observability_days <= max(
            self.message_days,
            self.patch_days,
            self.intervention_days,
        ):
            raise ValueError(
                "observability retention must exceed content retention"
            )


@dataclass(frozen=True, slots=True)
class AIRetentionReport:
    checkpoints: int = 0
    memories: int = 0
    messages: int = 0
    legacy_messages: int = 0
    patches: int = 0
    interventions: int = 0
    deleted_conversations: int = 0
    observability_events: int = 0

    @property
    def total(self) -> int:
        return sum(asdict(self).values())


async def _delete_returning(
    session: AsyncSession,
    statement: Any,
    id_column: Any,
) -> int:
    result = await session.execute(statement.returning(id_column))
    return len(list(result.scalars()))


def _normalize_now(now: datetime | None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    return current.astimezone(timezone.utc)


async def purge_expired_ai_data(
    session: AsyncSession,
    *,
    now: datetime | None = None,
    policy: AIRetentionPolicy | None = None,
) -> AIRetentionReport:
    """Apply the retention policy in one caller-owned transaction."""

    current = _normalize_now(now)
    selected_policy = policy or AIRetentionPolicy.from_settings()

    checkpoints = await _delete_returning(
        session,
        delete(AIGraphCheckpoint).where(AIGraphCheckpoint.expires_at <= current),
        AIGraphCheckpoint.id,
    )
    memories = await _delete_returning(
        session,
        delete(AIMemory).where(
            AIMemory.expires_at.is_not(None),
            AIMemory.expires_at <= current,
        ),
        AIMemory.id,
    )

    expiring_request_ids = select(AIProposedPatch.request_id).where(
        AIProposedPatch.status == "pending",
        AIProposedPatch.expires_at <= current,
    )
    await session.execute(
        update(AIMessage)
        .where(
            AIMessage.role == "assistant",
            AIMessage.request_id.in_(expiring_request_ids),
        )
        .values(
            patch_status="expired",
            requires_confirmation=False,
        )
    )
    await session.execute(
        update(AIProposedPatch)
        .where(
            AIProposedPatch.status == "pending",
            AIProposedPatch.expires_at <= current,
        )
        .values(status="expired")
    )

    message_cutoff = current - timedelta(days=selected_policy.message_days)
    messages = await _delete_returning(
        session,
        delete(AIMessage).where(AIMessage.created_at < message_cutoff),
        AIMessage.id,
    )
    legacy_messages = await _delete_returning(
        session,
        delete(ChatMessage).where(ChatMessage.created_at < message_cutoff),
        ChatMessage.id,
    )

    intervention_cutoff = current - timedelta(
        days=selected_policy.intervention_days
    )
    interventions = await _delete_returning(
        session,
        delete(AIIntervention).where(
            AIIntervention.created_at < intervention_cutoff
        ),
        AIIntervention.id,
    )

    retained_decision_patch_ids = select(
        AIFeedbackerDecisionMemory.patch_id
    )
    resolved_patch_cutoff = current - timedelta(
        days=selected_policy.patch_days
    )
    expired_patch_cutoff = current - timedelta(
        days=selected_policy.expired_patch_grace_days
    )
    patches = await _delete_returning(
        session,
        delete(AIProposedPatch).where(
            AIProposedPatch.id.not_in(retained_decision_patch_ids),
            or_(
                (
                    AIProposedPatch.status.in_(("pending", "expired"))
                    & (AIProposedPatch.expires_at < expired_patch_cutoff)
                ),
                (
                    (AIProposedPatch.status == "applied")
                    & (AIProposedPatch.applied_at < resolved_patch_cutoff)
                ),
                (
                    (AIProposedPatch.status == "rejected")
                    & (AIProposedPatch.rejected_at < resolved_patch_cutoff)
                ),
            ),
        ),
        AIProposedPatch.id,
    )

    deleted_conversation_cutoff = current - timedelta(
        days=selected_policy.deleted_conversation_days
    )
    deleted_conversations = await _delete_returning(
        session,
        delete(AIConversation).where(
            AIConversation.deleted_at.is_not(None),
            AIConversation.deleted_at < deleted_conversation_cutoff,
        ),
        AIConversation.id,
    )

    observability_cutoff = current - timedelta(
        days=selected_policy.observability_days
    )
    observability_events = await _delete_returning(
        session,
        delete(AIUsageEvent).where(
            AIUsageEvent.created_at < observability_cutoff
        ),
        AIUsageEvent.id,
    )

    return AIRetentionReport(
        checkpoints=checkpoints,
        memories=memories,
        messages=messages,
        legacy_messages=legacy_messages,
        patches=patches,
        interventions=interventions,
        deleted_conversations=deleted_conversations,
        observability_events=observability_events,
    )


async def _run() -> None:
    try:
        async with async_session_maker() as session:
            async with session.begin():
                report = await purge_expired_ai_data(session)
        print(json.dumps({**asdict(report), "total": report.total}, sort_keys=True))
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
