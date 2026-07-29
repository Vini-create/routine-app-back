import asyncio
from uuid import uuid4

import pytest

from app.ai.domain.enums import InternalRoute
from app.ai.schemas.responses import AIInvokeResponse, AIUsage
from app.api import ai_routes
from app.api.ai_routes import _stream_word_chunks
from app.api.dependencies import get_current_verified_user
from app.api.main import app
from app.billing.models import BillingAccount
from app.models.auth import User


def test_stream_word_chunks_preserves_the_message_for_incremental_rendering() -> None:
    message = "Olá, Vini!\nVamos organizar seu dia?"

    chunks = _stream_word_chunks(message)

    assert chunks == ["Olá, ", "Vini!\n", "Vamos ", "organizar ", "seu ", "dia?"]
    assert "".join(chunks) == message


class _SlowSuccessfulOrchestrator:
    async def invoke(self, payload, *, is_stream: bool = False) -> AIInvokeResponse:
        del payload
        assert is_stream is True
        await asyncio.sleep(0.02)
        return AIInvokeResponse(
            request_id=uuid4(),
            conversation_id=uuid4(),
            route=InternalRoute.ALFRED,
            message="Resposta concluída.",
            usage=AIUsage(
                plan="free",
                units_reserved=1,
                units_consumed=1,
                units_remaining=None,
            ),
        )


@pytest.mark.asyncio
async def test_stream_sends_heartbeats_while_the_graph_is_still_running(
    client,
    session,
    monkeypatch,
) -> None:
    user = User(
        email="stream-heartbeat@example.com",
        display_name="Stream heartbeat",
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

    async def current_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = current_user_override
    monkeypatch.setattr(ai_routes, "STREAM_HEARTBEAT_SECONDS", 0.001)
    monkeypatch.setattr(
        ai_routes,
        "_orchestrator",
        lambda _session, _user: _SlowSuccessfulOrchestrator(),
    )

    response = await client.post(
        "/api/v1/ai/stream",
        json={"message": "Olá", "selected_skill": "conversar"},
    )

    assert response.status_code == 200
    assert "event: heartbeat" in response.text
    assert "event: token" in response.text
    assert "event: done" in response.text
