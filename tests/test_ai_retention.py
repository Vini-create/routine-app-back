"""Retention tests for transient Alfred content and long-lived observability."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.ai.maintenance.retention import AIRetentionPolicy, purge_expired_ai_data
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
from app.models.auth import User

NOW = datetime(2026, 7, 26, 12, tzinfo=timezone.utc)

pytestmark = pytest.mark.asyncio


def _conversation(user_id, *, deleted_at=None) -> AIConversation:
    return AIConversation(
        user_id=user_id,
        title="Retention test",
        deleted_at=deleted_at,
        created_at=NOW - timedelta(days=200),
        updated_at=NOW,
    )


def _patch(
    *,
    user_id,
    conversation_id,
    status: str,
    resolved_at: datetime | None,
) -> AIProposedPatch:
    return AIProposedPatch(
        request_id=uuid4(),
        user_id=user_id,
        conversation_id=conversation_id,
        status=status,
        entity_type="routine_item",
        entity_id=uuid4(),
        operations=[
            {
                "op": "replace",
                "path": "/duration_minutes",
                "value": 30,
            }
        ],
        reason="Reduce routine load.",
        simulation={"before": {}, "after": {}},
        success_metrics=[],
        expires_at=NOW - timedelta(days=100),
        applied_at=resolved_at if status == "applied" else None,
        rejected_at=resolved_at if status == "rejected" else None,
        created_at=NOW - timedelta(days=100),
    )


async def test_retention_policy_rejects_short_observability_window() -> None:
    with pytest.raises(ValueError, match="observability"):
        AIRetentionPolicy(
            message_days=90,
            patch_days=90,
            expired_patch_grace_days=7,
            deleted_conversation_days=30,
            intervention_days=180,
            observability_days=180,
        )


async def test_cleanup_deletes_expired_content_but_keeps_recent_and_metrics(
    session,
) -> None:
    user = User(
        email="ai-retention@example.com",
        display_name="Retention",
        timezone="UTC",
        language="en",
    )
    session.add(user)
    await session.flush()

    active_conversation = _conversation(user.id)
    deleted_conversation = _conversation(
        user.id,
        deleted_at=NOW - timedelta(days=31),
    )
    session.add_all([active_conversation, deleted_conversation])
    await session.flush()

    old_message = AIMessage(
        conversation_id=active_conversation.id,
        user_id=user.id,
        role="user",
        content="Old raw content",
        request_id=uuid4(),
        created_at=NOW - timedelta(days=91),
    )
    recent_message = AIMessage(
        conversation_id=active_conversation.id,
        user_id=user.id,
        role="assistant",
        content="Recent raw content",
        request_id=uuid4(),
        created_at=NOW - timedelta(days=1),
    )
    deleted_conversation_message = AIMessage(
        conversation_id=deleted_conversation.id,
        user_id=user.id,
        role="user",
        content="Deleted conversation",
        request_id=uuid4(),
        created_at=NOW - timedelta(days=1),
    )
    old_legacy_message = ChatMessage(
        user_id=user.id,
        role="user",
        content="Legacy old content",
        created_at=NOW - timedelta(days=91),
    )
    recent_legacy_message = ChatMessage(
        user_id=user.id,
        role="user",
        content="Legacy recent content",
        created_at=NOW - timedelta(days=1),
    )
    session.add_all(
        [
            old_message,
            recent_message,
            deleted_conversation_message,
            old_legacy_message,
            recent_legacy_message,
        ]
    )

    expired_checkpoint = AIGraphCheckpoint(
        request_id=uuid4(),
        user_id=user.id,
        conversation_id=active_conversation.id,
        status="completed",
        state={},
        response={},
        expires_at=NOW - timedelta(seconds=1),
    )
    current_checkpoint = AIGraphCheckpoint(
        request_id=uuid4(),
        user_id=user.id,
        conversation_id=active_conversation.id,
        status="completed",
        state={},
        response={},
        expires_at=NOW + timedelta(hours=1),
    )
    session.add_all([expired_checkpoint, current_checkpoint])

    expired_memory = AIMemory(
        user_id=user.id,
        conversation_id=active_conversation.id,
        memory_type="short_term",
        content="Expired memory",
        content_fingerprint="a" * 64,
        confidence=Decimal("0.700"),
        importance=Decimal("0.500"),
        source_request_id=uuid4(),
        expires_at=NOW - timedelta(seconds=1),
    )
    current_memory = AIMemory(
        user_id=user.id,
        conversation_id=active_conversation.id,
        memory_type="semantic",
        content="Current memory",
        content_fingerprint="b" * 64,
        confidence=Decimal("0.700"),
        importance=Decimal("0.500"),
        source_request_id=uuid4(),
        expires_at=NOW + timedelta(days=1),
    )
    session.add_all([expired_memory, current_memory])

    old_intervention = AIIntervention(
        user_id=user.id,
        request_id=uuid4(),
        intervention_type="legacy",
        before_metrics={},
        expected_metrics=[],
        evaluation_due_at=NOW - timedelta(days=190),
        created_at=NOW - timedelta(days=181),
    )
    recent_intervention = AIIntervention(
        user_id=user.id,
        request_id=uuid4(),
        intervention_type="recent",
        before_metrics={},
        expected_metrics=[],
        evaluation_due_at=NOW,
        created_at=NOW - timedelta(days=1),
    )
    session.add_all([old_intervention, recent_intervention])

    expired_patch = _patch(
        user_id=user.id,
        conversation_id=active_conversation.id,
        status="expired",
        resolved_at=None,
    )
    old_applied_patch = _patch(
        user_id=user.id,
        conversation_id=active_conversation.id,
        status="applied",
        resolved_at=NOW - timedelta(days=91),
    )
    remembered_patch = _patch(
        user_id=user.id,
        conversation_id=active_conversation.id,
        status="rejected",
        resolved_at=NOW - timedelta(days=91),
    )
    session.add_all([expired_patch, old_applied_patch, remembered_patch])
    await session.flush()
    session.add(
        AIFeedbackerDecisionMemory(
            user_id=user.id,
            patch_id=remembered_patch.id,
            adjustment_type="routine_item:duration_minutes",
            context="Reduce routine load.",
            decision="rejected",
            reason="Not now.",
            inferred_preference="Avoid repeating without new evidence.",
            confidence=Decimal("0.850"),
            created_at=NOW - timedelta(days=91),
        )
    )

    old_usage = AIUsageEvent(
        request_id=uuid4(),
        user_id=user.id,
        route="alfred",
        plan_code="free",
        reserved_units=1,
        consumed_units=1,
        status="consumed",
        created_at=NOW - timedelta(days=401),
    )
    retained_usage = AIUsageEvent(
        request_id=uuid4(),
        user_id=user.id,
        route="feedbacker",
        plan_code="free",
        reserved_units=1,
        consumed_units=1,
        status="consumed",
        created_at=NOW - timedelta(days=399),
    )
    session.add_all([old_usage, retained_usage])
    await session.commit()

    report = await purge_expired_ai_data(session, now=NOW)
    await session.commit()

    assert report.checkpoints == 1
    assert report.memories == 1
    assert report.messages == 1
    assert report.legacy_messages == 1
    assert report.patches == 2
    assert report.interventions == 1
    assert report.deleted_conversations == 1
    assert report.observability_events == 1
    assert report.total == 9

    assert await session.get(AIMessage, recent_message.id) is not None
    assert await session.get(ChatMessage, recent_legacy_message.id) is not None
    assert await session.get(AIGraphCheckpoint, current_checkpoint.id) is not None
    assert await session.get(AIMemory, current_memory.id) is not None
    assert await session.get(AIIntervention, recent_intervention.id) is not None
    assert await session.get(AIProposedPatch, remembered_patch.id) is not None
    assert await session.get(AIUsageEvent, retained_usage.id) is not None
    assert await session.scalar(
        select(func.count(AIFeedbackerDecisionMemory.id)).where(
            AIFeedbackerDecisionMemory.user_id == user.id
        )
    ) == 1
