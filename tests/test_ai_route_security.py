"""Security contract and end-to-end smoke tests for every public AI route."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.ai.repositories.persistence_repository import create_conversation
from app.ai.schemas.patches import PatchOperation, ProposedPatch
from app.ai.services.patch_service import (
    persist_pending_patch,
    validate_and_simulate_patch,
)
from app.api.ai_routes import (
    get_current_ai_billing_access,
)
from app.api.dependencies import get_current_user, get_current_verified_user
from app.api.main import app
from app.api.rate_limit import limiter
from app.billing.models import BillingAccount
from app.models.ai import AIConversation, AIProposedPatch
from app.models.auth import User
from app.models.routine import RoutineItem

pytestmark = pytest.mark.asyncio


@dataclass(frozen=True, slots=True)
class RouteCase:
    method: str
    path: str
    payload: dict[str, Any] | None = None


RESOURCE_ID = UUID("11111111-1111-4111-8111-111111111111")
IDEMPOTENCY_KEY = UUID("22222222-2222-4222-8222-222222222222")

AI_ROUTE_CASES = (
    RouteCase(
        "POST",
        "/api/v1/ai/invoke",
        {"message": "Quantos hábitos ativos eu tenho?", "selected_skill": "auto"},
    ),
    RouteCase(
        "POST",
        "/api/v1/ai/stream",
        {"message": "Quantos hábitos ativos eu tenho?", "selected_skill": "auto"},
    ),
    RouteCase("GET", "/api/v1/ai/usage"),
    RouteCase("GET", "/api/v1/ai/capabilities"),
    RouteCase(
        "POST",
        f"/api/v1/ai/patches/{RESOURCE_ID}/accept",
        {"idempotency_key": str(IDEMPOTENCY_KEY)},
    ),
    RouteCase(
        "POST",
        f"/api/v1/ai/patches/{RESOURCE_ID}/reject",
        {"reason": "Prefiro manter como está."},
    ),
    RouteCase(
        "POST",
        f"/api/v1/ai/patches/{RESOURCE_ID}/edit",
        {
            "idempotency_key": str(IDEMPOTENCY_KEY),
            "operations": [
                {"op": "replace", "path": "/duration_minutes", "value": 45}
            ],
        },
    ),
    RouteCase("POST", "/api/v1/ai/conversations", {"title": "Teste seguro"}),
    RouteCase("GET", "/api/v1/ai/conversations"),
    RouteCase("GET", f"/api/v1/ai/conversations/{RESOURCE_ID}"),
    RouteCase("DELETE", f"/api/v1/ai/conversations/{RESOURCE_ID}"),
)

EXPECTED_ROUTE_TEMPLATES = {
    ("POST", "/api/v1/ai/invoke"),
    ("POST", "/api/v1/ai/stream"),
    ("GET", "/api/v1/ai/usage"),
    ("GET", "/api/v1/ai/capabilities"),
    ("POST", "/api/v1/ai/patches/{patch_id}/accept"),
    ("POST", "/api/v1/ai/patches/{patch_id}/reject"),
    ("POST", "/api/v1/ai/patches/{patch_id}/edit"),
    ("POST", "/api/v1/ai/conversations"),
    ("GET", "/api/v1/ai/conversations"),
    ("GET", "/api/v1/ai/conversations/{conversation_id}"),
    ("DELETE", "/api/v1/ai/conversations/{conversation_id}"),
}


def _dependency_calls(dependant: Dependant) -> set[Any]:
    calls: set[Any] = set()
    for child in dependant.dependencies:
        if child.call is not None:
            calls.add(child.call)
        calls.update(_dependency_calls(child))
    return calls


def _public_ai_routes() -> list[APIRoute]:
    return [
        route
        for route in app.routes
        if isinstance(route, APIRoute) and route.path.startswith("/api/v1/ai")
    ]


async def _create_user(
    session,
    *,
    email: str,
    verified: bool = True,
    with_active_plan: bool = False,
) -> User:
    user = User(
        email=email,
        display_name="AI Route Security",
        timezone="America/Sao_Paulo",
        language="portuguese_br",
        is_active=True,
        is_verified=verified,
        signature_plan="free",
    )
    session.add(user)
    await session.flush()
    if with_active_plan:
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


async def _pending_patch(
    session,
    *,
    user: User,
    title: str,
) -> tuple[RoutineItem, AIProposedPatch]:
    conversation = await create_conversation(
        session,
        user_id=user.id,
        title_source=title,
    )
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
    proposal = ProposedPatch(
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
        patch=proposal,
    )
    patch = await persist_pending_patch(
        session,
        request_id=uuid4(),
        user_id=user.id,
        conversation_id=conversation.id,
        patch=proposal,
        simulation=simulation,
    )
    await session.commit()
    await session.refresh(routine)
    await session.refresh(patch)
    return routine, patch


async def _request(client, case: RouteCase):
    return await client.request(
        case.method,
        case.path,
        json=case.payload,
    )


async def test_every_public_ai_route_has_the_complete_security_contract() -> None:
    routes = _public_ai_routes()
    actual_templates = {
        (method, route.path)
        for route in routes
        for method in route.methods
        if method in {"GET", "POST", "DELETE"}
    }

    assert actual_templates == EXPECTED_ROUTE_TEMPLATES
    for route in routes:
        dependencies = _dependency_calls(route.dependant)
        assert get_current_verified_user in dependencies, route.path
        assert get_current_ai_billing_access in dependencies, route.path
        limiter_key = f"{route.endpoint.__module__}.{route.endpoint.__name__}"
        assert limiter_key in limiter._route_limits, route.path
        assert limiter._route_limits[limiter_key], route.path


@pytest.mark.parametrize("case", AI_ROUTE_CASES)
async def test_every_ai_route_rejects_anonymous_access(client, case: RouteCase) -> None:
    response = await _request(client, case)

    assert response.status_code in {401, 403}


@pytest.mark.parametrize("case", AI_ROUTE_CASES)
async def test_every_ai_route_rejects_unverified_users(
    client,
    session,
    case: RouteCase,
) -> None:
    user = await _create_user(
        session,
        email=f"unverified-{AI_ROUTE_CASES.index(case)}@example.com",
        verified=False,
    )

    async def current_user_override() -> User:
        return user

    app.dependency_overrides[get_current_user] = current_user_override
    response = await _request(client, case)

    assert response.status_code == 403
    assert response.json()["detail"] == "Email not verified"


@pytest.mark.parametrize("case", AI_ROUTE_CASES)
async def test_every_ai_route_fails_closed_without_an_active_plan(
    client,
    session,
    case: RouteCase,
) -> None:
    user = await _create_user(
        session,
        email=f"no-plan-{AI_ROUTE_CASES.index(case)}@example.com",
    )

    async def verified_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = verified_user_override
    response = await _request(client, case)

    assert response.status_code == 403
    assert response.json()["code"] == "plan_unavailable"


async def test_all_ai_routes_work_with_verified_active_free_user(
    client,
    session,
) -> None:
    user = await _create_user(
        session,
        email="all-ai-routes@example.com",
        with_active_plan=True,
    )

    async def verified_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = verified_user_override

    invoke = await client.post(
        "/api/v1/ai/invoke",
        json={
            "message": "Quantos hábitos ativos eu tenho?",
            "selected_skill": "auto",
        },
    )
    assert invoke.status_code == 200, invoke.text
    assert invoke.json()["route"] == "deterministic"

    stream = await client.post(
        "/api/v1/ai/stream",
        json={
            "message": "Quantos hábitos ativos eu tenho?",
            "selected_skill": "auto",
        },
    )
    assert stream.status_code == 200, stream.text
    assert "event: done" in stream.text

    usage = await client.get("/api/v1/ai/usage")
    assert usage.status_code == 200, usage.text
    assert usage.json()["plan"] == "free"

    capabilities = await client.get("/api/v1/ai/capabilities")
    assert capabilities.status_code == 200, capabilities.text
    assert capabilities.json()["capabilities"]["patch_generation"] is True

    created = await client.post(
        "/api/v1/ai/conversations",
        json={"title": "Conversa protegida"},
    )
    assert created.status_code == 201, created.text
    conversation_id = created.json()["id"]

    listed = await client.get("/api/v1/ai/conversations")
    assert listed.status_code == 200, listed.text
    assert conversation_id in {item["id"] for item in listed.json()}

    detail = await client.get(f"/api/v1/ai/conversations/{conversation_id}")
    assert detail.status_code == 200, detail.text
    assert detail.json()["id"] == conversation_id

    accepted_routine, accepted_patch = await _pending_patch(
        session,
        user=user,
        title="Patch aceito",
    )
    accepted = await client.post(
        f"/api/v1/ai/patches/{accepted_patch.id}/accept",
        json={"idempotency_key": str(uuid4())},
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "applied"
    await session.refresh(accepted_routine)
    assert accepted_routine.duration_minutes == 30

    _rejected_routine, rejected_patch = await _pending_patch(
        session,
        user=user,
        title="Patch rejeitado",
    )
    rejected = await client.post(
        f"/api/v1/ai/patches/{rejected_patch.id}/reject",
        json={"reason": "Não combina com a minha rotina."},
    )
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["status"] == "rejected"

    _edited_routine, edited_patch = await _pending_patch(
        session,
        user=user,
        title="Patch editado",
    )
    edited = await client.post(
        f"/api/v1/ai/patches/{edited_patch.id}/edit",
        json={
            "idempotency_key": str(uuid4()),
            "operations": [
                {"op": "replace", "path": "/duration_minutes", "value": 45}
            ],
        },
    )
    assert edited.status_code == 200, edited.text
    assert edited.json()["status"] == "pending"
    assert edited.json()["requires_confirmation"] is True
    assert edited.json()["proposed_patch"]["simulation"]["after"][
        "duration_minutes"
    ] == 45

    deleted = await client.delete(f"/api/v1/ai/conversations/{conversation_id}")
    assert deleted.status_code == 204, deleted.text
    missing_after_delete = await client.get(
        f"/api/v1/ai/conversations/{conversation_id}"
    )
    assert missing_after_delete.status_code == 404


async def test_ai_resource_ownership_is_enforced_at_the_http_boundary(
    client,
    session,
) -> None:
    owner = await _create_user(
        session,
        email="ai-resource-owner@example.com",
        with_active_plan=True,
    )
    attacker = await _create_user(
        session,
        email="ai-resource-attacker@example.com",
        with_active_plan=True,
    )
    conversation = AIConversation(user_id=owner.id, title="Somente do dono")
    session.add(conversation)
    _routine, patch = await _pending_patch(
        session,
        user=owner,
        title="Patch somente do dono",
    )
    await session.commit()
    await session.refresh(conversation)

    async def attacker_override() -> User:
        return attacker

    app.dependency_overrides[get_current_verified_user] = attacker_override

    conversation_response = await client.get(
        f"/api/v1/ai/conversations/{conversation.id}"
    )
    delete_response = await client.delete(
        f"/api/v1/ai/conversations/{conversation.id}"
    )
    patch_response = await client.post(
        f"/api/v1/ai/patches/{patch.id}/accept",
        json={"idempotency_key": str(uuid4())},
    )

    assert conversation_response.status_code == 403
    assert conversation_response.json()["code"] == "conversation_forbidden"
    assert delete_response.status_code == 403
    assert delete_response.json()["code"] == "conversation_forbidden"
    assert patch_response.status_code == 403
    assert patch_response.json()["code"] == "patch_forbidden"


async def test_write_rate_limit_is_enforced_at_runtime(client, session) -> None:
    user = await _create_user(
        session,
        email="ai-http-rate-limit@example.com",
        with_active_plan=True,
    )

    async def verified_user_override() -> User:
        return user

    app.dependency_overrides[get_current_verified_user] = verified_user_override
    limiter.reset()
    app.state.limiter.enabled = True
    missing_conversation_id = uuid4()
    try:
        for _index in range(20):
            response = await client.delete(
                f"/api/v1/ai/conversations/{missing_conversation_id}"
            )
            assert response.status_code == 404, response.text

        limited = await client.delete(
            f"/api/v1/ai/conversations/{missing_conversation_id}"
        )
        assert limited.status_code == 429
    finally:
        app.state.limiter.enabled = False
        limiter.reset()
