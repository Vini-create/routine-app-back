"""Transactional quota, burst and concurrent-stream protection."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.enums import InternalRoute
from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.billing.entitlements import get_route_unit_cost
from app.billing.enums import UsageEventStatus
from app.billing.service import BillingAccess, require_active_billing_access
from app.core.config import settings
from app.models.ai import AIUsageEvent

STANDARD_ROUTES = frozenset(
    {
        InternalRoute.DETERMINISTIC,
        InternalRoute.ALFRED,
    }
)
RAG_ROUTES = frozenset(
    {
        InternalRoute.RAG_THEN_ALFRED,
        InternalRoute.RAG_THEN_FEEDBACKER,
    }
)
DEEP_ANALYSIS_ROUTES = frozenset(
    {
        InternalRoute.FEEDBACKER,
        InternalRoute.RAG_THEN_FEEDBACKER,
    }
)


@dataclass(frozen=True, slots=True)
class UsageReservation:
    event: AIUsageEvent
    idempotent_replay: bool = False


@dataclass(frozen=True, slots=True)
class QuotaUsage:
    used: int
    limit: int | None
    remaining: int | None
    reset_at: datetime


@dataclass(frozen=True, slots=True)
class UsageSnapshot:
    plan: str
    weighted_units_today: QuotaUsage
    standard_requests_today: QuotaUsage
    rag_requests_today: QuotaUsage
    deep_analyses_this_week: QuotaUsage
    requests_per_minute: int


def _normalize_now(now: datetime | None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return current.astimezone(timezone.utc)


def _local_day_bounds(now: datetime, timezone_name: str) -> tuple[datetime, datetime]:
    try:
        local_now = now.astimezone(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        local_now = now.astimezone(timezone.utc)

    local_start = datetime.combine(local_now.date(), time.min, tzinfo=local_now.tzinfo)
    local_end = local_start + timedelta(days=1)
    return local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc)


def _local_week_bounds(
    now: datetime,
    timezone_name: str,
) -> tuple[datetime, datetime]:
    try:
        local_now = now.astimezone(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        local_now = now.astimezone(timezone.utc)

    week_start_date = local_now.date() - timedelta(days=local_now.weekday())
    local_start = datetime.combine(
        week_start_date,
        time.min,
        tzinfo=local_now.tzinfo,
    )
    local_end = local_start + timedelta(days=7)
    return local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc)


async def _find_existing_reservation(
    session: AsyncSession,
    *,
    user_id: UUID,
    request_id: UUID,
    idempotency_key: UUID | None,
) -> AIUsageEvent | None:
    replay_conditions = [AIUsageEvent.request_id == request_id]
    if idempotency_key is not None:
        replay_conditions.append(AIUsageEvent.idempotency_key == idempotency_key)
    result = await session.execute(
        select(AIUsageEvent).where(
            AIUsageEvent.user_id == user_id,
            or_(*replay_conditions),
        )
    )
    return result.scalars().first()


async def _release_expired_reservations(
    session: AsyncSession,
    *,
    user_id: UUID,
    now: datetime,
) -> None:
    await session.execute(
        update(AIUsageEvent)
        .where(
            AIUsageEvent.user_id == user_id,
            AIUsageEvent.status == UsageEventStatus.RESERVED.value,
            AIUsageEvent.reservation_expires_at <= now,
        )
        .values(
            status=UsageEventStatus.RELEASED.value,
            completed_at=now,
            error_code="reservation_expired",
        )
    )


async def _used_units_between(
    session: AsyncSession,
    *,
    user_id: UUID,
    start: datetime,
    end: datetime,
    now: datetime,
) -> int:
    chargeable_units = case(
        (
            and_(
                AIUsageEvent.status == UsageEventStatus.RESERVED.value,
                AIUsageEvent.reservation_expires_at > now,
            ),
            AIUsageEvent.reserved_units,
        ),
        (
            AIUsageEvent.status.in_(
                [
                    UsageEventStatus.CONSUMED.value,
                    UsageEventStatus.FAILED.value,
                ]
            ),
            AIUsageEvent.consumed_units,
        ),
        else_=0,
    )
    used = await session.scalar(
        select(func.coalesce(func.sum(chargeable_units), 0)).where(
            AIUsageEvent.user_id == user_id,
            AIUsageEvent.created_at >= start,
            AIUsageEvent.created_at < end,
        )
    )
    return int(used or 0)


async def _count_route_usage_between(
    session: AsyncSession,
    *,
    user_id: UUID,
    routes: frozenset[InternalRoute],
    start: datetime,
    end: datetime,
    now: datetime,
) -> int:
    route_values = [route.value for route in routes]
    chargeable_event = or_(
        AIUsageEvent.status == UsageEventStatus.CONSUMED.value,
        and_(
            AIUsageEvent.status == UsageEventStatus.RESERVED.value,
            AIUsageEvent.reservation_expires_at > now,
        ),
        and_(
            AIUsageEvent.status == UsageEventStatus.FAILED.value,
            AIUsageEvent.consumed_units > 0,
        ),
    )
    count = await session.scalar(
        select(func.count(AIUsageEvent.id)).where(
            AIUsageEvent.user_id == user_id,
            AIUsageEvent.route.in_(route_values),
            AIUsageEvent.created_at >= start,
            AIUsageEvent.created_at < end,
            chargeable_event,
        )
    )
    return int(count or 0)


async def _global_cost_today(
    session: AsyncSession,
    *,
    now: datetime,
) -> Decimal:
    utc_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    cost = await session.scalar(
        select(func.coalesce(func.sum(AIUsageEvent.estimated_cost), 0)).where(
            AIUsageEvent.created_at >= utc_start,
            AIUsageEvent.status.in_(
                [
                    UsageEventStatus.CONSUMED.value,
                    UsageEventStatus.FAILED.value,
                ]
            ),
        )
    )
    return Decimal(cost or 0)


def _limit_error(
    code: AIErrorCode,
    message: str,
    request_id: UUID,
) -> AIApplicationError:
    return AIApplicationError(code, message, request_id=str(request_id))


async def reserve_ai_usage(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    route: InternalRoute,
    timezone_name: str,
    conversation_id: UUID | None = None,
    idempotency_key: UUID | None = None,
    is_stream: bool = False,
    now: datetime | None = None,
) -> UsageReservation:
    """Atomically validate the plan and reserve weighted units."""

    current = _normalize_now(now)
    try:
        access = await require_active_billing_access(
            session,
            user_id,
            for_update=True,
            request_id=request_id,
        )
        existing = await _find_existing_reservation(
            session,
            user_id=user_id,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            await session.commit()
            return UsageReservation(existing, idempotent_replay=True)

        await _release_expired_reservations(
            session,
            user_id=user_id,
            now=current,
        )
        await _validate_burst_limit(session, access, user_id, request_id, current)
        await _validate_stream_limit(
            session,
            access,
            user_id,
            request_id,
            current,
            is_stream,
        )

        reserved_units = get_route_unit_cost(route)
        day_start, day_end = _local_day_bounds(current, timezone_name)
        week_start, week_end = _local_week_bounds(current, timezone_name)
        await _validate_category_limits(
            session,
            access=access,
            user_id=user_id,
            route=route,
            request_id=request_id,
            day_start=day_start,
            day_end=day_end,
            week_start=week_start,
            week_end=week_end,
            now=current,
        )
        used_today = await _used_units_between(
            session,
            user_id=user_id,
            start=day_start,
            end=day_end,
            now=current,
        )
        unit_limit = access.entitlements.ai_units_per_day
        if unit_limit is not None and used_today + reserved_units > unit_limit:
            raise _limit_error(
                AIErrorCode.DAILY_QUOTA_EXCEEDED,
                "The daily AI unit quota has been reached",
                request_id,
            )

        global_cost = await _global_cost_today(session, now=current)
        if (
            reserved_units > 0
            and global_cost >= settings.ai_global_daily_cost_limit_usd
        ):
            raise _limit_error(
                AIErrorCode.GLOBAL_COST_LIMIT_EXCEEDED,
                "The global daily AI cost ceiling has been reached",
                request_id,
            )

        event = AIUsageEvent(
            request_id=request_id,
            idempotency_key=idempotency_key,
            user_id=user_id,
            conversation_id=conversation_id,
            route=route.value,
            plan_code=access.plan_code.value,
            reserved_units=reserved_units,
            consumed_units=0,
            status=UsageEventStatus.RESERVED.value,
            is_stream=is_stream,
            reservation_expires_at=current
            + timedelta(seconds=settings.ai_reservation_timeout_seconds),
            created_at=current,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return UsageReservation(event)
    except AIApplicationError:
        await session.rollback()
        raise
    except IntegrityError:
        await session.rollback()
        existing = await _find_existing_reservation(
            session,
            user_id=user_id,
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
        if existing is None:
            raise
        await session.commit()
        return UsageReservation(existing, idempotent_replay=True)


async def _validate_burst_limit(
    session: AsyncSession,
    access: BillingAccess,
    user_id: UUID,
    request_id: UUID,
    now: datetime,
) -> None:
    recent_requests = await session.scalar(
        select(func.count(AIUsageEvent.id)).where(
            AIUsageEvent.user_id == user_id,
            AIUsageEvent.created_at > now - timedelta(minutes=1),
            AIUsageEvent.created_at <= now,
        )
    )
    if int(recent_requests or 0) >= access.entitlements.requests_per_minute:
        raise _limit_error(
            AIErrorCode.RATE_LIMIT_EXCEEDED,
            "The per-minute AI request limit has been reached",
            request_id,
        )


async def _validate_category_limits(
    session: AsyncSession,
    *,
    access: BillingAccess,
    user_id: UUID,
    route: InternalRoute,
    request_id: UUID,
    day_start: datetime,
    day_end: datetime,
    week_start: datetime,
    week_end: datetime,
    now: datetime,
) -> None:
    standard_limit = access.entitlements.standard_requests_per_day
    if route in STANDARD_ROUTES and standard_limit is not None:
        standard_used = await _count_route_usage_between(
            session,
            user_id=user_id,
            routes=STANDARD_ROUTES,
            start=day_start,
            end=day_end,
            now=now,
        )
        if standard_used >= standard_limit:
            raise _limit_error(
                AIErrorCode.DAILY_STANDARD_LIMIT_EXCEEDED,
                "The daily deterministic and conversational limit has been reached",
                request_id,
            )

    rag_limit = access.entitlements.rag_requests_per_day
    if route in RAG_ROUTES and rag_limit is not None:
        rag_used = await _count_route_usage_between(
            session,
            user_id=user_id,
            routes=RAG_ROUTES,
            start=day_start,
            end=day_end,
            now=now,
        )
        if rag_used >= rag_limit:
            raise _limit_error(
                AIErrorCode.DAILY_RAG_LIMIT_EXCEEDED,
                "The daily RAG limit has been reached",
                request_id,
            )

    deep_limit = access.entitlements.deep_analyses_per_week
    if route in DEEP_ANALYSIS_ROUTES and deep_limit is not None:
        deep_used = await _count_route_usage_between(
            session,
            user_id=user_id,
            routes=DEEP_ANALYSIS_ROUTES,
            start=week_start,
            end=week_end,
            now=now,
        )
        if deep_used >= deep_limit:
            raise _limit_error(
                AIErrorCode.WEEKLY_DEEP_ANALYSIS_LIMIT_EXCEEDED,
                "The weekly deep analysis limit has been reached",
                request_id,
            )


async def _validate_stream_limit(
    session: AsyncSession,
    access: BillingAccess,
    user_id: UUID,
    request_id: UUID,
    now: datetime,
    is_stream: bool,
) -> None:
    if not is_stream:
        return
    concurrent_streams = await session.scalar(
        select(func.count(AIUsageEvent.id)).where(
            AIUsageEvent.user_id == user_id,
            AIUsageEvent.is_stream.is_(True),
            AIUsageEvent.status == UsageEventStatus.RESERVED.value,
            AIUsageEvent.reservation_expires_at > now,
        )
    )
    if int(concurrent_streams or 0) >= access.entitlements.max_concurrent_streams:
        raise _limit_error(
            AIErrorCode.CONCURRENT_STREAM_LIMIT_EXCEEDED,
            "The concurrent AI stream limit has been reached",
            request_id,
        )


async def confirm_ai_usage(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost: Decimal = Decimal("0"),
    latency_ms: int | None = None,
    now: datetime | None = None,
) -> AIUsageEvent:
    """Confirm a reservation exactly once after graph execution."""

    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts cannot be negative")
    if estimated_cost < 0:
        raise ValueError("estimated_cost cannot be negative")
    if latency_ms is not None and latency_ms < 0:
        raise ValueError("latency_ms cannot be negative")

    current = _normalize_now(now)
    event = await _get_owned_event_for_update(session, request_id, user_id)
    if event.status == UsageEventStatus.CONSUMED.value:
        await session.commit()
        return event
    if event.status != UsageEventStatus.RESERVED.value:
        await session.rollback()
        raise _limit_error(
            AIErrorCode.USAGE_RESERVATION_ALREADY_CLOSED,
            "The AI usage reservation is already closed",
            request_id,
        )

    event.status = UsageEventStatus.CONSUMED.value
    event.consumed_units = event.reserved_units
    event.input_tokens = input_tokens
    event.output_tokens = output_tokens
    event.estimated_cost = estimated_cost
    event.latency_ms = latency_ms
    event.completed_at = current
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def release_ai_usage(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    reason: str,
    now: datetime | None = None,
) -> AIUsageEvent:
    """Release units when execution stops before model or RAG usage."""

    return await _close_reservation(
        session,
        request_id=request_id,
        user_id=user_id,
        status=UsageEventStatus.RELEASED,
        consumed_units=0,
        reason=reason,
        now=now,
    )


async def fail_ai_usage(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    reason: str,
    charge_reserved_units: bool,
    now: datetime | None = None,
) -> AIUsageEvent:
    """Close a failed execution, charging only if expensive work started."""

    event = await _get_owned_event_for_update(session, request_id, user_id)
    return await _close_locked_event(
        session,
        event=event,
        request_id=request_id,
        status=UsageEventStatus.FAILED,
        consumed_units=event.reserved_units if charge_reserved_units else 0,
        reason=reason,
        now=now,
    )


async def _close_reservation(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    status: UsageEventStatus,
    consumed_units: int,
    reason: str,
    now: datetime | None,
) -> AIUsageEvent:
    event = await _get_owned_event_for_update(session, request_id, user_id)
    return await _close_locked_event(
        session,
        event=event,
        request_id=request_id,
        status=status,
        consumed_units=consumed_units,
        reason=reason,
        now=now,
    )


async def _close_locked_event(
    session: AsyncSession,
    *,
    event: AIUsageEvent,
    request_id: UUID,
    status: UsageEventStatus,
    consumed_units: int,
    reason: str,
    now: datetime | None,
) -> AIUsageEvent:
    if event.status == status.value:
        await session.commit()
        return event
    if event.status != UsageEventStatus.RESERVED.value:
        await session.rollback()
        raise _limit_error(
            AIErrorCode.USAGE_RESERVATION_ALREADY_CLOSED,
            "The AI usage reservation is already closed",
            request_id,
        )

    event.status = status.value
    event.consumed_units = consumed_units
    event.error_code = reason[:100]
    event.completed_at = _normalize_now(now)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def _get_owned_event_for_update(
    session: AsyncSession,
    request_id: UUID,
    user_id: UUID,
) -> AIUsageEvent:
    result = await session.execute(
        select(AIUsageEvent)
        .where(
            AIUsageEvent.request_id == request_id,
            AIUsageEvent.user_id == user_id,
        )
        .with_for_update()
    )
    event = result.scalar_one_or_none()
    if event is None:
        await session.rollback()
        raise _limit_error(
            AIErrorCode.USAGE_RESERVATION_NOT_FOUND,
            "The AI usage reservation was not found",
            request_id,
        )
    return event


async def get_usage_snapshot(
    session: AsyncSession,
    *,
    user_id: UUID,
    timezone_name: str,
    now: datetime | None = None,
) -> UsageSnapshot:
    current = _normalize_now(now)
    access = await require_active_billing_access(session, user_id)
    await _release_expired_reservations(session, user_id=user_id, now=current)
    day_start, day_end = _local_day_bounds(current, timezone_name)
    week_start, week_end = _local_week_bounds(current, timezone_name)
    weighted_units = await _used_units_between(
        session,
        user_id=user_id,
        start=day_start,
        end=day_end,
        now=current,
    )
    standard_used = await _count_route_usage_between(
        session,
        user_id=user_id,
        routes=STANDARD_ROUTES,
        start=day_start,
        end=day_end,
        now=current,
    )
    rag_used = await _count_route_usage_between(
        session,
        user_id=user_id,
        routes=RAG_ROUTES,
        start=day_start,
        end=day_end,
        now=current,
    )
    deep_used = await _count_route_usage_between(
        session,
        user_id=user_id,
        routes=DEEP_ANALYSIS_ROUTES,
        start=week_start,
        end=week_end,
        now=current,
    )
    await session.commit()
    return UsageSnapshot(
        plan=access.plan_code.value,
        weighted_units_today=_quota_usage(
            weighted_units,
            access.entitlements.ai_units_per_day,
            day_end,
        ),
        standard_requests_today=_quota_usage(
            standard_used,
            access.entitlements.standard_requests_per_day,
            day_end,
        ),
        rag_requests_today=_quota_usage(
            rag_used,
            access.entitlements.rag_requests_per_day,
            day_end,
        ),
        deep_analyses_this_week=_quota_usage(
            deep_used,
            access.entitlements.deep_analyses_per_week,
            week_end,
        ),
        requests_per_minute=access.entitlements.requests_per_minute,
    )


def _quota_usage(used: int, limit: int | None, reset_at: datetime) -> QuotaUsage:
    return QuotaUsage(
        used=used,
        limit=limit,
        remaining=None if limit is None else max(0, limit - used),
        reset_at=reset_at,
    )
