"""Public integration coverage for every Alfred skill exposed by the frontend."""

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.ai.domain.enums import InternalRoute
from app.api.dependencies import get_current_verified_user
from app.api.main import app
from app.billing.models import BillingAccount
from app.models.ai import AIConversation
from app.models.auth import User

pytestmark = pytest.mark.asyncio


class SkillMatrixGraph:
    """Deterministic graph boundary: validates API orchestration, not an LLM."""

    async def ainvoke(self, state, config, *, context):
        del config, context
        route = state["route"].value
        return {
            **state,
            "detected_language": "pt-BR",
            "response_language": "pt-BR",
            "token_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "model_calls": 0,
                "by_role": {},
            },
            "final_response": {
                "route": route,
                "message": f"Resposta validada para {route}.",
                "references": [],
                "analysis": None,
                "proposed_patch": None,
                "requires_confirmation": False,
            },
        }


async def _free_user(session) -> User:
    user = User(
        email="skill-matrix@example.com",
        display_name="Skill matrix",
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


@pytest.mark.parametrize(
    ("selected_skill", "message", "expected_route"),
    [
        ("auto", "Quantos hábitos ativos eu tenho?", InternalRoute.DETERMINISTIC),
        ("conversar", "Quero refletir sobre minha semana.", InternalRoute.ALFRED),
        (
            "analisar_progresso",
            "Quero entender meu progresso recente.",
            InternalRoute.FEEDBACKER,
        ),
        (
            "reorganizar_rotina",
            "Preciso revisar minha rotina atual.",
            InternalRoute.FEEDBACKER,
        ),
        (
            "criar_plano",
            "Quero estruturar um plano para esta meta.",
            InternalRoute.FEEDBACKER,
        ),
        (
            "consultar_conhecimento",
            "Quais práticas têm melhor evidência para foco?",
            InternalRoute.RAG_THEN_ALFRED,
        ),
    ],
)
async def test_every_frontend_skill_invokes_and_persists_a_response(
    client,
    session,
    monkeypatch,
    selected_skill: str,
    message: str,
    expected_route: InternalRoute,
) -> None:
    user = await _free_user(session)

    async def current_user_override() -> User:
        return user

    monkeypatch.setattr(
        "app.ai.services.orchestrator.default_graph",
        lambda: SkillMatrixGraph(),
    )
    # RAG construction is covered independently; this matrix verifies that its
    # public skill can traverse orchestration and persistence successfully.
    monkeypatch.setattr(
        "app.ai.services.orchestrator.build_default_knowledge_retriever",
        lambda: object(),
    )
    app.dependency_overrides[get_current_verified_user] = current_user_override

    response = await client.post(
        "/api/v1/ai/invoke",
        json={
            "message": message,
            "selected_skill": selected_skill,
            "idempotency_key": str(uuid4()),
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["route"] == expected_route.value
    assert body["message"] == f"Resposta validada para {expected_route.value}."
    assert body["conversation_id"]

    conversation_id = await session.scalar(
        select(AIConversation.id).where(AIConversation.user_id == user.id)
    )
    assert conversation_id is not None
    history = await client.get(f"/api/v1/ai/conversations/{conversation_id}")
    assert history.status_code == 200, history.text
    assistant_messages = [
        item
        for item in history.json()["messages"]
        if item["role"] == "assistant"
    ]
    assert assistant_messages[-1]["route"] == expected_route.value
    assert assistant_messages[-1]["content"] == body["message"]
