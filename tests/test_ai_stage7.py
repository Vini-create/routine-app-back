"""Stage 7 integration tests: public API, idempotency and safe HITL patches."""

from datetime import datetime, timedelta, timezone
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.ai.domain.enums import SelectedSkill
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.models.gateway import ModelInvocationResult, ModelRole, SchemaT
from app.ai.repositories.persistence_repository import (
    create_conversation,
    load_feedbacker_decision_memories,
)
from app.ai.schemas.patches import PatchOperation, ProposedPatch
from app.ai.schemas.alfred import AlfredIntervention
from app.ai.schemas.requests import AIInvokeRequest
from app.ai.services.orchestrator import AIOrchestrator
from app.ai.services.patch_service import (
    accept_patch,
    edit_patch,
    persist_pending_patch,
    reject_patch,
    validate_and_simulate_patch,
)
from app.api.dependencies import get_current_verified_user
from app.api.main import app
from app.billing.models import BillingAccount
from app.models.ai import (
    AIGraphCheckpoint,
    AIConversation,
    AIFeedbackerDecisionMemory,
    AIMemory,
    AIMessage,
    AIIntervention,
    AIPatchAudit,
    AIProposedPatch,
    AIUsageEvent,
)
from app.models.auth import User
from app.models.routine import RoutineItem

pytestmark = pytest.mark.asyncio


class SummaryModelGateway:
    def __init__(self) -> None:
        self.user_prompts: list[str] = []

    async def invoke_structured(
        self,
        *,
        role: ModelRole,
        schema: type[SchemaT],
        system_prompt: str,
        user_prompt: str,
    ) -> ModelInvocationResult[SchemaT]:
        assert role is ModelRole.ALFRED
        assert schema is AlfredIntervention
        assert "Security and authority" in system_prompt
        self.user_prompts.append(user_prompt)
        parsed = AlfredIntervention(
            strategy="practical_next_step",
            message="Vamos escolher uma ação pequena.",
            next_steps=["Escolher um hábito prioritário."],
            memory_candidates=[],
            updated_summary_en=(
                "The user wants a small practical action for this week."
            ),
        )
        return ModelInvocationResult(
            parsed=cast(SchemaT, parsed),
            model="fake-alfred",
            usage={
                "input_tokens": 100,
                "output_tokens": 25,
                "total_tokens": 125,
            },
        )


async def create_billed_user(session, email: str) -> User:
    user = User(
        email=email,
        display_name="Stage 7",
        timezone="America/Sao_Paulo",
        language="portuguese_br",
        is_active=True,
        is_verified=True,
        signature_plan="free",
    )
    session.add(user)
    await session.flush()
    session.add(
        BillingAccount(
            user_id=user.id,
            plan_code="free",
            subscription_status="active",
            billing_provider="internal",
        )
    )
    await session.commit()
    await session.refresh(user)
    return user


async def test_single_public_invoke_is_persisted_and_idempotent(
    client,
    session,
) -> None:
    user = await create_billed_user(session, "invoke-stage7@example.com")

    async def current_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = current_user_override
    idempotency_key = uuid4()
    payload = {
        "message": "Quantos hábitos ativos eu tenho?",
        "selected_skill": "auto",
        "idempotency_key": str(idempotency_key),
    }

    first = await client.post("/api/v1/ai/invoke", json=payload)
    assert first.status_code == 200, first.text
    first_body = first.json()
    assert first_body["route"] == "deterministic"
    assert first_body["usage"]["units_consumed"] == 0
    assert first_body["requires_confirmation"] is False

    replay = await client.post("/api/v1/ai/invoke", json=payload)
    assert replay.status_code == 200, replay.text
    assert replay.json() == first_body

    request_id = first_body["request_id"]
    assert await session.scalar(
        select(func.count(AIMessage.id)).where(AIMessage.request_id == request_id)
    ) == 2
    assert await session.scalar(
        select(func.count(AIUsageEvent.id)).where(
            AIUsageEvent.request_id == request_id
        )
    ) == 1
    checkpoint = await session.scalar(
        select(AIGraphCheckpoint).where(
            AIGraphCheckpoint.request_id == request_id
        )
    )
    assert checkpoint is not None
    assert checkpoint.status == "completed"
    assert checkpoint.response["request_id"] == request_id


async def test_stream_exposes_the_documented_sse_contract(client, session) -> None:
    user = await create_billed_user(session, "stream-stage7@example.com")

    async def current_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = current_user_override
    response = await client.post(
        "/api/v1/ai/stream",
        json={
            "message": "Quantos hábitos ativos eu tenho?",
            "selected_skill": "auto",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: status" in response.text
    assert "event: token" in response.text
    assert "event: done" in response.text


async def pending_routine_patch(
    session,
    *,
    user: User,
) -> tuple[RoutineItem, AIProposedPatch]:
    conversation = await create_conversation(
        session,
        user_id=user.id,
        title_source="Reorganizar rotina",
    )
    routine = RoutineItem(
        user_id=user.id,
        title="Estudo",
        item_type="task",
        schedule_type="single",
        start_at=datetime(2026, 7, 27, 9, tzinfo=timezone.utc),
        duration_minutes=60,
        status="active",
    )
    session.add(routine)
    await session.flush()
    draft = ProposedPatch(
        entity_type="routine_item",
        entity_id=routine.id,
        operations=[
            PatchOperation(
                op="replace",
                path="/duration_minutes",
                value=30,
            )
        ],
        reason="Reduzir a carga para facilitar consistência.",
        success_metrics=[
            {
                "name": "Taxa de conclusão",
                "target": "increase",
                "evaluation_window_days": 14,
            }
        ],
    )
    simulation = await validate_and_simulate_patch(
        session,
        user_id=user.id,
        patch=draft,
    )
    patch = await persist_pending_patch(
        session,
        request_id=uuid4(),
        user_id=user.id,
        conversation_id=conversation.id,
        patch=draft,
        simulation=simulation,
    )
    await session.commit()
    await session.refresh(routine)
    await session.refresh(patch)
    return routine, patch


async def test_patch_is_only_applied_after_confirmation_and_is_audited(
    session,
) -> None:
    user = await create_billed_user(session, "patch-accept@example.com")
    routine, patch = await pending_routine_patch(session, user=user)

    assert routine.duration_minutes == 60
    idempotency_key = uuid4()
    applied, audit = await accept_patch(
        session,
        patch_id=patch.id,
        user_id=user.id,
        idempotency_key=idempotency_key,
    )
    await session.refresh(routine)

    assert applied.status == "applied"
    assert routine.duration_minutes == 30
    assert audit.before_state["duration_minutes"] == 60
    assert audit.after_state["duration_minutes"] == 30
    replayed_patch, replayed_audit = await accept_patch(
        session,
        patch_id=patch.id,
        user_id=user.id,
        idempotency_key=idempotency_key,
    )
    assert replayed_patch.id == applied.id
    assert replayed_audit.id == audit.id
    assert await session.scalar(
        select(func.count(AIPatchAudit.id)).where(
            AIPatchAudit.patch_id == patch.id,
            AIPatchAudit.action == "applied",
        )
    ) == 1
    decision_memory = await session.scalar(
        select(AIFeedbackerDecisionMemory).where(
            AIFeedbackerDecisionMemory.patch_id == patch.id
        )
    )
    assert decision_memory is not None
    assert decision_memory.decision == "accepted"
    assert decision_memory.adjustment_type == "routine_item:duration_minutes"
    assert await session.scalar(select(func.count(AIIntervention.id))) == 0


async def test_patch_edit_revalidates_and_requires_confirmation_again(session) -> None:
    user = await create_billed_user(session, "patch-edit@example.com")
    routine, patch = await pending_routine_patch(session, user=user)

    edited = await edit_patch(
        session,
        patch_id=patch.id,
        user_id=user.id,
        idempotency_key=uuid4(),
        operations=[
            PatchOperation(
                op="replace",
                path="/duration_minutes",
                value=45,
            )
        ],
    )
    await session.refresh(routine)

    assert edited.status == "pending"
    assert edited.simulation["after"]["duration_minutes"] == 45
    assert routine.duration_minutes == 60


async def test_patch_reject_expire_and_cross_user_guards(session) -> None:
    owner = await create_billed_user(session, "patch-owner@example.com")
    other = await create_billed_user(session, "patch-attacker@example.com")
    _routine, patch = await pending_routine_patch(session, user=owner)
    patch_id = patch.id
    owner_id = owner.id
    other_id = other.id

    with pytest.raises(AIApplicationError) as forbidden:
        await accept_patch(
            session,
            patch_id=patch_id,
            user_id=other_id,
            idempotency_key=uuid4(),
        )
    assert forbidden.value.code is AIErrorCode.PATCH_FORBIDDEN

    rejected, audit = await reject_patch(
        session,
        patch_id=patch_id,
        user_id=owner_id,
        reason="Prefiro manter a rotina.",
    )
    assert rejected.status == "rejected"
    assert audit.action == "rejected"
    decision_memory = await session.scalar(
        select(AIFeedbackerDecisionMemory).where(
            AIFeedbackerDecisionMemory.patch_id == patch_id
        )
    )
    assert decision_memory is not None
    assert decision_memory.reason == "Prefiro manter a rotina."
    assert float(decision_memory.confidence) == pytest.approx(0.85)

    owner = await session.get(User, owner_id)
    assert owner is not None
    _other_routine, expiring = await pending_routine_patch(session, user=owner)
    expiring.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    session.add(expiring)
    await session.commit()
    with pytest.raises(AIApplicationError) as expired:
        await accept_patch(
            session,
            patch_id=expiring.id,
            user_id=owner_id,
            idempotency_key=uuid4(),
        )
    assert expired.value.code is AIErrorCode.PATCH_EXPIRED
    stored = await session.get(AIProposedPatch, expiring.id)
    assert stored is not None
    assert stored.status == "expired"


async def test_feedbacker_keeps_only_the_four_newest_decisions(session) -> None:
    user = await create_billed_user(session, "bounded-memory@example.com")
    base_time = datetime(2026, 7, 26, 12, tzinfo=timezone.utc)

    for index in range(5):
        _routine, patch = await pending_routine_patch(session, user=user)
        await reject_patch(
            session,
            patch_id=patch.id,
            user_id=user.id,
            reason=f"reason-{index}",
            now=base_time + timedelta(minutes=index),
        )

    memories = await load_feedbacker_decision_memories(
        session,
        user_id=user.id,
    )

    assert len(memories) == 4
    assert [memory["reason"] for memory in memories] == [
        "reason-4",
        "reason-3",
        "reason-2",
        "reason-1",
    ]
    assert await session.scalar(
        select(func.count(AIFeedbackerDecisionMemory.id)).where(
            AIFeedbackerDecisionMemory.user_id == user.id
        )
    ) == 4


async def test_orchestrator_atomically_replaces_and_reuses_rolling_summary(
    session,
) -> None:
    user = await create_billed_user(session, "rolling-summary@example.com")
    first_gateway = SummaryModelGateway()
    first_response = await AIOrchestrator(
        session=session,
        user=user,
        model_gateway=first_gateway,
    ).invoke(
        AIInvokeRequest(
            message="Me ajude a escolher uma ação pequena.",
            selected_skill=SelectedSkill.CONVERSAR,
        )
    )

    conversation = await session.get(
        AIConversation,
        first_response.conversation_id,
    )
    assert conversation is not None
    assert (
        conversation.summary_en
        == "The user wants a small practical action for this week."
    )

    second_gateway = SummaryModelGateway()
    await AIOrchestrator(
        session=session,
        user=user,
        model_gateway=second_gateway,
    ).invoke(
        AIInvokeRequest(
            conversation_id=conversation.id,
            message="Agora me ajude a continuar.",
            selected_skill=SelectedSkill.CONVERSAR,
        )
    )

    assert "The user wants a small practical action for this week." in (
        second_gateway.user_prompts[0]
    )


async def test_no_public_feedbacker_route_exists() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/v1/ai/invoke" in paths
    assert "/api/v1/ai/stream" in paths
    assert not any("feedbacker" in path.casefold() for path in paths)
    assert AIMemory.__tablename__ == "ai_memories"
