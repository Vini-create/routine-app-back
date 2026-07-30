"""Reload-safe structured artifacts for Alfred's unified conversation history."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.maintenance.retention import purge_expired_ai_data
from app.ai.repositories.persistence_repository import create_conversation
from app.ai.schemas.patches import PatchOperation, ProposedPatch
from app.ai.services.patch_service import (
    accept_patch,
    edit_patch,
    persist_pending_patch,
    public_patch,
    reject_patch,
    validate_and_simulate_patch,
)
from app.api.dependencies import get_current_verified_user
from app.api.main import app
from app.billing.models import BillingAccount
from app.models.ai import AIConversation, AIMessage, AIProposedPatch
from app.models.auth import User
from app.models.routine import RoutineItem

pytestmark = pytest.mark.asyncio


async def _create_user(session, *, email: str) -> User:
    user = User(
        email=email,
        display_name="History artifacts",
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


def _analysis() -> dict:
    return {
        "diagnosis": {
            "summary": "A execução caiu nos dias de maior carga.",
            "data_window": "últimos 30 dias",
            "data_quality": 0.9,
            "observed_facts": ["Queda de conclusão às quartas-feiras."],
        },
        "patterns": [
            {
                "name": "Sobrecarga no meio da semana",
                "description": "Há mais itens do que tempo disponível.",
                "evidence": ["Três atrasos consecutivos."],
                "confidence": 0.82,
            }
        ],
        "hypotheses": [],
        "recommendations": [],
        "success_metrics": [],
        "metadata": {"route_agnostic": True},
    }


def _references() -> list[dict]:
    return [
        {
            "document_id": "guide-1",
            "chunk_id": "chunk-3",
            "title": "Guia de consistência",
            "source": "knowledge://guides/consistency",
            "source_ids": ["guide-1"],
            "topic": "consistência",
            "supporting_excerpt": "Ajustes menores favorecem a continuidade.",
            "retrieval_score": 0.91,
            "rerank_score": 0.88,
        }
    ]


def _serialized_patch() -> dict:
    return {
        "patch_id": str(uuid4()),
        "entity_type": "profile",
        "entity_id": str(uuid4()),
        "operations": [
            {"op": "replace", "path": "/name", "value": "Plano sustentável"}
        ],
        "reason": "Adequar o plano à carga observada.",
        "simulation": {
            "status": "validated",
            "before": {"name": "Plano atual"},
            "after": {"name": "Plano sustentável"},
            "changed_fields": ["name"],
        },
        "success_metrics": [],
    }


class _ArtifactGraph:
    def __init__(self) -> None:
        self.patch = _serialized_patch()

    async def ainvoke(self, state, config, *, context):
        del config, context
        return {
            **state,
            "detected_language": "pt-BR",
            "response_language": "pt-BR",
            "token_usage": {
                "input_tokens": 120,
                "output_tokens": 80,
                "total_tokens": 200,
                "model_calls": 1,
                "by_role": {},
            },
            "final_response": {
                "route": "feedbacker",
                "message": "Encontrei uma oportunidade de ajuste.",
                "analysis": _analysis(),
                "references": _references(),
                "proposed_patch": self.patch,
                "requires_confirmation": True,
            },
        }


@pytest.mark.parametrize("endpoint", ["invoke", "stream"])
async def test_invoke_and_stream_artifacts_survive_history_reload(
    client,
    session,
    monkeypatch,
    endpoint: str,
) -> None:
    user = await _create_user(
        session,
        email=f"history-{endpoint}@example.com",
    )

    async def current_user_override() -> User:
        return user

    graph = _ArtifactGraph()
    monkeypatch.setattr(
        "app.ai.services.orchestrator.default_graph",
        lambda: graph,
    )
    app.dependency_overrides[get_current_verified_user] = current_user_override

    response = await client.post(
        f"/api/v1/ai/{endpoint}",
        json={
            "message": "Analise profundamente meu progresso recente.",
            "selected_skill": "analisar_progresso",
        },
    )
    assert response.status_code == 200, response.text

    conversation_id = await session.scalar(
        select(AIConversation.id).where(AIConversation.user_id == user.id)
    )
    assert conversation_id is not None
    history = await client.get(
        f"/api/v1/ai/conversations/{conversation_id}"
    )
    assert history.status_code == 200, history.text
    assistant = next(
        item
        for item in history.json()["messages"]
        if item["role"] == "assistant"
    )

    assert assistant["analysis"] == _analysis()
    assert len(assistant["references"]) == len(_references())
    for persisted, expected in zip(
        assistant["references"],
        _references(),
        strict=True,
    ):
        assert {
            key: persisted[key]
            for key in expected
        } == expected
    assert assistant["proposed_patch"] == graph.patch
    assert assistant["requires_confirmation"] is True
    assert assistant["patch_status"] == "pending"


async def _pending_patch_with_message(
    session,
    *,
    user: User,
    conversation: AIConversation,
    title: str,
) -> tuple[RoutineItem, AIProposedPatch]:
    routine = RoutineItem(
        user_id=user.id,
        title=title,
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
    session.add(
        AIMessage(
            conversation_id=conversation.id,
            user_id=user.id,
            role="assistant",
            content="Sugestão pendente.",
            route="feedbacker",
            request_id=patch.request_id,
            proposed_patch=public_patch(patch).model_dump(mode="json"),
            requires_confirmation=True,
            patch_status="pending",
        )
    )
    await session.commit()
    await session.refresh(patch)
    return routine, patch


async def test_patch_lifecycle_is_reflected_after_history_reload(
    client,
    session,
) -> None:
    user = await _create_user(session, email="patch-history@example.com")
    conversation = await create_conversation(
        session,
        user_id=user.id,
        title_source="Histórico de patches",
    )

    _edited_routine, edited_patch = await _pending_patch_with_message(
        session,
        user=user,
        conversation=conversation,
        title="Patch editado e aceito",
    )
    await edit_patch(
        session,
        patch_id=edited_patch.id,
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
    await accept_patch(
        session,
        patch_id=edited_patch.id,
        user_id=user.id,
        idempotency_key=uuid4(),
    )

    _rejected_routine, rejected_patch = await _pending_patch_with_message(
        session,
        user=user,
        conversation=conversation,
        title="Patch rejeitado",
    )
    await reject_patch(
        session,
        patch_id=rejected_patch.id,
        user_id=user.id,
        reason="Não cabe na rotina.",
    )

    _expired_routine, expired_patch = await _pending_patch_with_message(
        session,
        user=user,
        conversation=conversation,
        title="Patch expirado",
    )
    expired_patch.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    session.add(expired_patch)
    await session.commit()
    with pytest.raises(AIApplicationError) as expired:
        await accept_patch(
            session,
            patch_id=expired_patch.id,
            user_id=user.id,
            idempotency_key=uuid4(),
        )
    assert expired.value.code is AIErrorCode.PATCH_EXPIRED

    _job_routine, job_expired_patch = await _pending_patch_with_message(
        session,
        user=user,
        conversation=conversation,
        title="Patch expirado pelo job",
    )
    job_expired_patch.expires_at = datetime.now(timezone.utc) - timedelta(
        seconds=1
    )
    session.add(job_expired_patch)
    await session.commit()
    await purge_expired_ai_data(session)
    await session.commit()

    async def current_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = current_user_override
    response = await client.get(
        f"/api/v1/ai/conversations/{conversation.id}"
    )
    assert response.status_code == 200, response.text
    by_request_id = {
        item["request_id"]: item for item in response.json()["messages"]
    }

    applied = by_request_id[str(edited_patch.request_id)]
    assert applied["patch_status"] == "applied"
    assert applied["requires_confirmation"] is False
    assert applied["proposed_patch"]["simulation"]["after"][
        "duration_minutes"
    ] == 45

    rejected = by_request_id[str(rejected_patch.request_id)]
    assert rejected["patch_status"] == "rejected"
    assert rejected["requires_confirmation"] is False

    expired_by_request = by_request_id[str(expired_patch.request_id)]
    assert expired_by_request["patch_status"] == "expired"
    assert expired_by_request["requires_confirmation"] is False

    expired_by_job = by_request_id[str(job_expired_patch.request_id)]
    assert expired_by_job["patch_status"] == "expired"
    assert expired_by_job["requires_confirmation"] is False


async def test_legacy_nullable_messages_and_artifacts_remain_private(
    client,
    session,
) -> None:
    owner = await _create_user(session, email="history-owner@example.com")
    attacker = await _create_user(session, email="history-attacker@example.com")
    conversation = await create_conversation(
        session,
        user_id=owner.id,
        title_source="Mensagem antiga",
    )
    request_id = uuid4()
    session.add_all(
        [
            AIMessage(
                conversation_id=conversation.id,
                user_id=owner.id,
                role="user",
                content="Mensagem criada antes dos artefatos.",
                request_id=request_id,
            ),
            AIMessage(
                conversation_id=conversation.id,
                user_id=owner.id,
                role="assistant",
                content="Resposta antiga.",
                request_id=request_id,
            ),
        ]
    )
    await session.commit()

    async def owner_override() -> User:
        return owner

    app.dependency_overrides[get_current_verified_user] = owner_override
    owner_response = await client.get(
        f"/api/v1/ai/conversations/{conversation.id}"
    )
    assert owner_response.status_code == 200
    for message in owner_response.json()["messages"]:
        assert message["analysis"] is None
        assert message["references"] is None
        assert message["proposed_patch"] is None
        assert message["requires_confirmation"] is None
        assert message["patch_status"] is None

    async def attacker_override() -> User:
        return attacker

    app.dependency_overrides[get_current_verified_user] = attacker_override
    attacker_response = await client.get(
        f"/api/v1/ai/conversations/{conversation.id}"
    )
    assert attacker_response.status_code == 403
    assert "Resposta antiga." not in attacker_response.text
