from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.ai.domain.enums import InternalRoute
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.ai.services.usage_service import (
    confirm_ai_usage,
    fail_ai_usage,
    get_usage_snapshot,
    release_ai_usage,
    reserve_ai_usage,
)
from app.billing.entitlements import (
    PLAN_ENTITLEMENTS,
    PlanEntitlements,
    get_plan_entitlements,
    get_route_unit_cost,
)
from app.billing.enums import (
    BillingProviderCode,
    PlanCode,
    SubscriptionStatus,
    UsageEventStatus,
)
from app.billing.models import BillingAccount
from app.billing.provider import BillingProviderError, InternalBillingProvider
from app.billing.repository import build_free_billing_account
from app.core.config import settings
from app.models.ai import AIUsageEvent
from app.models.auth import User
from app.services.auth_service import register_user

pytestmark = pytest.mark.asyncio

BASE_TIME = datetime(2026, 7, 26, 12, tzinfo=timezone.utc)


async def create_billed_user(
    session,
    *,
    email: str = "billing@example.com",
    plan_code: PlanCode = PlanCode.FREE,
    subscription_status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    timezone_name: str = "America/Sao_Paulo",
) -> tuple[User, BillingAccount]:
    user = User(
        email=email,
        display_name="Billing User",
        language="portuguese_br",
        timezone=timezone_name,
        signature_plan="free",
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    await session.flush()
    account = BillingAccount(
        user_id=user.id,
        plan_code=plan_code.value,
        subscription_status=subscription_status.value,
        billing_provider=BillingProviderCode.INTERNAL.value,
    )
    session.add(account)
    await session.commit()
    await session.refresh(user)
    await session.refresh(account)
    return user, account


async def reserve(
    session,
    user: User,
    route: InternalRoute,
    *,
    now: datetime = BASE_TIME,
    request_id=None,
    idempotency_key=None,
    is_stream: bool = False,
):
    return await reserve_ai_usage(
        session,
        request_id=request_id or uuid4(),
        user_id=user.id,
        route=route,
        timezone_name=user.timezone,
        idempotency_key=idempotency_key,
        is_stream=is_stream,
        now=now,
    )


async def test_free_entitlements_are_portfolio_friendly_and_immutable() -> None:
    free = get_plan_entitlements(PlanCode.FREE)

    assert free == PlanEntitlements(
        requests_per_minute=6,
        ai_units_per_day=None,
        standard_requests_per_day=30,
        rag_requests_per_day=15,
        deep_analyses_per_week=3,
        max_concurrent_streams=1,
        rag_enabled=True,
        patch_generation_enabled=True,
        memory_level="basic",
        max_input_chars=4_000,
    )
    with pytest.raises(FrozenInstanceError):
        free.ai_units_per_day = 999  # type: ignore[misc]
    with pytest.raises(TypeError):
        PLAN_ENTITLEMENTS[PlanCode.FREE] = free  # type: ignore[index]


async def test_all_weighted_route_costs_match_the_contract() -> None:
    assert {route: get_route_unit_cost(route) for route in InternalRoute} == {
        InternalRoute.SAFE_RESPONSE: 0,
        InternalRoute.DETERMINISTIC: 0,
        InternalRoute.ALFRED: 1,
        InternalRoute.FEEDBACKER: 3,
        InternalRoute.RAG_THEN_ALFRED: 2,
        InternalRoute.RAG_THEN_FEEDBACKER: 4,
    }


async def test_unknown_plan_and_route_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unsupported plan"):
        get_plan_entitlements("enterprise")
    with pytest.raises(ValueError, match="Unsupported internal route"):
        get_route_unit_cost("unknown")


async def test_internal_provider_never_creates_external_billing_resources() -> None:
    provider = InternalBillingProvider()
    user = User(email="provider@example.com")

    with pytest.raises(BillingProviderError):
        await provider.create_customer(user)
    with pytest.raises(BillingProviderError):
        await provider.create_checkout_session(user=user, plan_code=PlanCode.PRO)
    with pytest.raises(BillingProviderError):
        await provider.create_customer_portal("customer")
    with pytest.raises(BillingProviderError):
        await provider.parse_webhook(payload=b"{}", signature="test")


async def test_password_registration_creates_free_billing_account_atomically(
    session,
) -> None:
    user, _credentials = await register_user(
        session,
        "registered@example.com",
        "Registered",
        "portuguese_br",
        "correct-password",
    )

    account = (
        await session.execute(
            select(BillingAccount).where(BillingAccount.user_id == user.id)
        )
    ).scalar_one()
    assert account.plan_code == PlanCode.FREE.value
    assert account.subscription_status == SubscriptionStatus.ACTIVE.value
    assert account.billing_provider == BillingProviderCode.INTERNAL.value
    assert account.provider_customer_id is None
    assert account.provider_subscription_id is None


async def test_missing_or_inactive_billing_account_fails_closed(session) -> None:
    user = User(email="missing-billing@example.com")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user_id = user.id

    with pytest.raises(AIApplicationError) as missing:
        await reserve(session, user, InternalRoute.ALFRED)
    assert missing.value.code is AIErrorCode.PLAN_UNAVAILABLE

    session.add(build_free_billing_account(user_id))
    await session.commit()
    account = (
        await session.execute(
            select(BillingAccount).where(BillingAccount.user_id == user_id)
        )
    ).scalar_one()
    account.subscription_status = SubscriptionStatus.CANCELED.value
    await session.commit()
    await session.refresh(user)

    with pytest.raises(AIApplicationError) as inactive:
        await reserve(session, user, InternalRoute.ALFRED)
    assert inactive.value.code is AIErrorCode.PLAN_UNAVAILABLE


@pytest.mark.parametrize(
    ("route", "expected_units"),
    [
        (InternalRoute.SAFE_RESPONSE, 0),
        (InternalRoute.DETERMINISTIC, 0),
        (InternalRoute.ALFRED, 1),
        (InternalRoute.RAG_THEN_ALFRED, 2),
        (InternalRoute.FEEDBACKER, 3),
        (InternalRoute.RAG_THEN_FEEDBACKER, 4),
    ],
)
async def test_reservation_and_confirmation_charge_route_weight(
    session,
    route: InternalRoute,
    expected_units: int,
) -> None:
    user, _account = await create_billed_user(session)
    reservation = await reserve(session, user, route)

    assert reservation.event.reserved_units == expected_units
    assert reservation.event.consumed_units == 0
    assert reservation.event.status == UsageEventStatus.RESERVED.value

    confirmed = await confirm_ai_usage(
        session,
        request_id=reservation.event.request_id,
        user_id=user.id,
        input_tokens=100,
        output_tokens=50,
        estimated_cost=Decimal("0.0025"),
        latency_ms=350,
        now=BASE_TIME + timedelta(seconds=1),
    )
    assert confirmed.status == UsageEventStatus.CONSUMED.value
    assert confirmed.consumed_units == expected_units
    assert confirmed.input_tokens == 100
    assert confirmed.output_tokens == 50
    assert confirmed.estimated_cost == Decimal("0.002500")


async def test_idempotency_key_does_not_reserve_twice(session) -> None:
    user, _account = await create_billed_user(session)
    idempotency_key = uuid4()
    first = await reserve(
        session,
        user,
        InternalRoute.FEEDBACKER,
        idempotency_key=idempotency_key,
    )
    second = await reserve(
        session,
        user,
        InternalRoute.FEEDBACKER,
        request_id=uuid4(),
        idempotency_key=idempotency_key,
    )

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True
    assert second.event.id == first.event.id
    count = await session.scalar(
        select(func.count(AIUsageEvent.id)).where(AIUsageEvent.user_id == user.id)
    )
    assert count == 1


async def test_confirm_is_idempotent(session) -> None:
    user, _account = await create_billed_user(session)
    reservation = await reserve(session, user, InternalRoute.ALFRED)

    first = await confirm_ai_usage(
        session,
        request_id=reservation.event.request_id,
        user_id=user.id,
        input_tokens=10,
        now=BASE_TIME + timedelta(seconds=1),
    )
    second = await confirm_ai_usage(
        session,
        request_id=reservation.event.request_id,
        user_id=user.id,
        input_tokens=999,
        now=BASE_TIME + timedelta(seconds=2),
    )

    assert second.id == first.id
    assert second.input_tokens == 10
    assert second.consumed_units == 1


async def test_free_plan_allows_thirty_standard_requests_per_day(session) -> None:
    user, _account = await create_billed_user(session)

    for index in range(30):
        current = BASE_TIME + timedelta(minutes=index * 2)
        route = InternalRoute.DETERMINISTIC if index % 2 == 0 else InternalRoute.ALFRED
        reservation = await reserve(session, user, route, now=current)
        await confirm_ai_usage(
            session,
            request_id=reservation.event.request_id,
            user_id=user.id,
            now=current + timedelta(seconds=1),
        )

    with pytest.raises(AIApplicationError) as exceeded:
        await reserve(
            session,
            user,
            InternalRoute.ALFRED,
            now=BASE_TIME + timedelta(minutes=60),
        )
    assert exceeded.value.code is AIErrorCode.DAILY_STANDARD_LIMIT_EXCEEDED

    # A safety response must remain available even when the normal quota ends.
    await session.refresh(user)
    safe = await reserve(
        session,
        user,
        InternalRoute.SAFE_RESPONSE,
        now=BASE_TIME + timedelta(minutes=60),
    )
    assert safe.event.reserved_units == 0


async def test_free_plan_allows_fifteen_rag_requests_per_day(session) -> None:
    user, _account = await create_billed_user(session)

    for index in range(15):
        current = BASE_TIME + timedelta(minutes=index * 2)
        reservation = await reserve(
            session,
            user,
            InternalRoute.RAG_THEN_ALFRED,
            now=current,
        )
        await confirm_ai_usage(
            session,
            request_id=reservation.event.request_id,
            user_id=user.id,
            now=current + timedelta(seconds=1),
        )

    with pytest.raises(AIApplicationError) as exceeded:
        await reserve(
            session,
            user,
            InternalRoute.RAG_THEN_ALFRED,
            now=BASE_TIME + timedelta(minutes=30),
        )
    assert exceeded.value.code is AIErrorCode.DAILY_RAG_LIMIT_EXCEEDED


async def test_free_plan_allows_three_deep_analyses_per_local_week(session) -> None:
    user, _account = await create_billed_user(session)
    routes = [
        InternalRoute.FEEDBACKER,
        InternalRoute.RAG_THEN_FEEDBACKER,
        InternalRoute.FEEDBACKER,
    ]

    for index, route in enumerate(routes):
        current = BASE_TIME + timedelta(minutes=index * 2)
        reservation = await reserve(session, user, route, now=current)
        await confirm_ai_usage(
            session,
            request_id=reservation.event.request_id,
            user_id=user.id,
            now=current + timedelta(seconds=1),
        )

    with pytest.raises(AIApplicationError) as exceeded:
        await reserve(
            session,
            user,
            InternalRoute.FEEDBACKER,
            now=BASE_TIME + timedelta(minutes=6),
        )
    assert exceeded.value.code is AIErrorCode.WEEKLY_DEEP_ANALYSIS_LIMIT_EXCEEDED

    await session.refresh(user)
    next_local_week = datetime(2026, 7, 27, 3, 1, tzinfo=timezone.utc)
    next_week_reservation = await reserve(
        session,
        user,
        InternalRoute.FEEDBACKER,
        now=next_local_week,
    )
    assert next_week_reservation.event.reserved_units == 3


async def test_paid_plans_keep_the_weighted_daily_unit_ceiling(session) -> None:
    user, _account = await create_billed_user(
        session,
        plan_code=PlanCode.PRO,
    )
    session.add(
        AIUsageEvent(
            request_id=uuid4(),
            user_id=user.id,
            route=InternalRoute.ALFRED.value,
            plan_code=PlanCode.PRO.value,
            reserved_units=200,
            consumed_units=200,
            status=UsageEventStatus.CONSUMED.value,
            created_at=BASE_TIME,
        )
    )
    await session.commit()

    with pytest.raises(AIApplicationError) as exceeded:
        await reserve(
            session,
            user,
            InternalRoute.ALFRED,
            now=BASE_TIME + timedelta(minutes=2),
        )
    assert exceeded.value.code is AIErrorCode.DAILY_QUOTA_EXCEEDED


async def test_per_minute_limit_counts_zero_unit_routes(session) -> None:
    user, _account = await create_billed_user(session)

    for index in range(6):
        current = BASE_TIME + timedelta(seconds=index)
        reservation = await reserve(
            session,
            user,
            InternalRoute.DETERMINISTIC,
            now=current,
        )
        await confirm_ai_usage(
            session,
            request_id=reservation.event.request_id,
            user_id=user.id,
            now=current,
        )

    with pytest.raises(AIApplicationError) as exceeded:
        await reserve(
            session,
            user,
            InternalRoute.DETERMINISTIC,
            now=BASE_TIME + timedelta(seconds=10),
        )
    assert exceeded.value.code is AIErrorCode.RATE_LIMIT_EXCEEDED


async def test_free_plan_allows_only_one_active_stream(session) -> None:
    user, _account = await create_billed_user(session)
    first = await reserve(
        session,
        user,
        InternalRoute.ALFRED,
        is_stream=True,
    )
    first_request_id = first.event.request_id
    user_id = user.id

    with pytest.raises(AIApplicationError) as concurrent:
        await reserve(
            session,
            user,
            InternalRoute.ALFRED,
            request_id=uuid4(),
            is_stream=True,
        )
    assert concurrent.value.code is AIErrorCode.CONCURRENT_STREAM_LIMIT_EXCEEDED

    released = await release_ai_usage(
        session,
        request_id=first_request_id,
        user_id=user_id,
        reason="client_disconnected_before_model",
        now=BASE_TIME + timedelta(seconds=1),
    )
    assert released.status == UsageEventStatus.RELEASED.value
    assert released.consumed_units == 0
    await session.refresh(user)

    replacement = await reserve(
        session,
        user,
        InternalRoute.ALFRED,
        request_id=uuid4(),
        is_stream=True,
        now=BASE_TIME + timedelta(seconds=2),
    )
    assert replacement.event.status == UsageEventStatus.RESERVED.value


async def test_expired_stream_reservation_releases_itself(session, monkeypatch) -> None:
    monkeypatch.setattr(settings, "ai_reservation_timeout_seconds", 30)
    user, _account = await create_billed_user(session)
    expired = await reserve(
        session,
        user,
        InternalRoute.ALFRED,
        is_stream=True,
    )

    replacement = await reserve(
        session,
        user,
        InternalRoute.ALFRED,
        request_id=uuid4(),
        is_stream=True,
        now=BASE_TIME + timedelta(seconds=31),
    )

    await session.refresh(expired.event)
    assert expired.event.status == UsageEventStatus.RELEASED.value
    assert expired.event.error_code == "reservation_expired"
    assert replacement.event.status == UsageEventStatus.RESERVED.value


@pytest.mark.parametrize(
    ("charge_reserved_units", "expected_units"),
    [(False, 0), (True, 3)],
)
async def test_failed_execution_charges_only_after_expensive_work_started(
    session,
    charge_reserved_units: bool,
    expected_units: int,
) -> None:
    user, _account = await create_billed_user(session)
    reservation = await reserve(session, user, InternalRoute.FEEDBACKER)

    failed = await fail_ai_usage(
        session,
        request_id=reservation.event.request_id,
        user_id=user.id,
        reason="model_timeout",
        charge_reserved_units=charge_reserved_units,
        now=BASE_TIME + timedelta(seconds=1),
    )
    assert failed.status == UsageEventStatus.FAILED.value
    assert failed.consumed_units == expected_units
    assert failed.error_code == "model_timeout"


async def test_user_cannot_confirm_another_users_reservation(session) -> None:
    owner, _account = await create_billed_user(session)
    attacker, _attacker_account = await create_billed_user(
        session,
        email="attacker@example.com",
    )
    reservation = await reserve(session, owner, InternalRoute.ALFRED)

    with pytest.raises(AIApplicationError) as forbidden:
        await confirm_ai_usage(
            session,
            request_id=reservation.event.request_id,
            user_id=attacker.id,
        )
    assert forbidden.value.code is AIErrorCode.USAGE_RESERVATION_NOT_FOUND


async def test_usage_snapshot_resets_at_users_local_midnight(session) -> None:
    user, _account = await create_billed_user(session)
    reservation = await reserve(session, user, InternalRoute.FEEDBACKER)
    await confirm_ai_usage(
        session,
        request_id=reservation.event.request_id,
        user_id=user.id,
        now=BASE_TIME + timedelta(seconds=1),
    )

    snapshot = await get_usage_snapshot(
        session,
        user_id=user.id,
        timezone_name=user.timezone,
        now=BASE_TIME + timedelta(minutes=1),
    )
    assert snapshot.plan == "free"
    assert snapshot.weighted_units_today.used == 3
    assert snapshot.weighted_units_today.limit is None
    assert snapshot.weighted_units_today.remaining is None
    assert snapshot.standard_requests_today.used == 0
    assert snapshot.standard_requests_today.limit == 30
    assert snapshot.rag_requests_today.used == 0
    assert snapshot.rag_requests_today.limit == 15
    assert snapshot.deep_analyses_this_week.used == 1
    assert snapshot.deep_analyses_this_week.limit == 3
    assert snapshot.deep_analyses_this_week.remaining == 2
    assert snapshot.requests_per_minute == 6
    assert snapshot.standard_requests_today.reset_at == datetime(
        2026,
        7,
        27,
        3,
        tzinfo=timezone.utc,
    )


async def test_rag_deep_analysis_counts_both_quotas_and_release_counts_neither(
    session,
) -> None:
    user, _account = await create_billed_user(session)
    consumed = await reserve(
        session,
        user,
        InternalRoute.RAG_THEN_FEEDBACKER,
    )
    await confirm_ai_usage(
        session,
        request_id=consumed.event.request_id,
        user_id=user.id,
        now=BASE_TIME + timedelta(seconds=1),
    )
    released = await reserve(
        session,
        user,
        InternalRoute.RAG_THEN_FEEDBACKER,
        now=BASE_TIME + timedelta(minutes=2),
    )
    await release_ai_usage(
        session,
        request_id=released.event.request_id,
        user_id=user.id,
        reason="client_disconnected",
        now=BASE_TIME + timedelta(minutes=2, seconds=1),
    )

    snapshot = await get_usage_snapshot(
        session,
        user_id=user.id,
        timezone_name=user.timezone,
        now=BASE_TIME + timedelta(minutes=3),
    )

    assert snapshot.rag_requests_today.used == 1
    assert snapshot.deep_analyses_this_week.used == 1
    assert snapshot.weighted_units_today.used == 4


async def test_global_cost_ceiling_blocks_new_paid_work(
    session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "ai_global_daily_cost_limit_usd",
        Decimal("0.01"),
    )
    user, _account = await create_billed_user(session)
    reservation = await reserve(session, user, InternalRoute.ALFRED)
    await confirm_ai_usage(
        session,
        request_id=reservation.event.request_id,
        user_id=user.id,
        estimated_cost=Decimal("0.01"),
        now=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(AIApplicationError) as ceiling:
        await reserve(
            session,
            user,
            InternalRoute.ALFRED,
            now=BASE_TIME + timedelta(minutes=2),
        )
    assert ceiling.value.code is AIErrorCode.GLOBAL_COST_LIMIT_EXCEEDED
    await session.refresh(user)

    free_route = await reserve(
        session,
        user,
        InternalRoute.DETERMINISTIC,
        now=BASE_TIME + timedelta(minutes=2),
    )
    assert free_route.event.reserved_units == 0
