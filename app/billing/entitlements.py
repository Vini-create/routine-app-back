"""Immutable plan capabilities and weighted route costs."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping

from app.ai.domain.enums import InternalRoute
from app.billing.enums import PlanCode

MemoryLevel = Literal["basic", "advanced"]


@dataclass(frozen=True, slots=True)
class PlanEntitlements:
    requests_per_minute: int
    ai_units_per_day: int | None
    standard_requests_per_day: int | None
    rag_requests_per_day: int | None
    deep_analyses_per_week: int | None
    max_concurrent_streams: int
    rag_enabled: bool
    patch_generation_enabled: bool
    memory_level: MemoryLevel
    max_input_chars: int


PLAN_ENTITLEMENTS: Mapping[PlanCode, PlanEntitlements] = MappingProxyType(
    {
        PlanCode.FREE: PlanEntitlements(
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
        ),
        PlanCode.PRO: PlanEntitlements(
            requests_per_minute=20,
            ai_units_per_day=200,
            standard_requests_per_day=None,
            rag_requests_per_day=None,
            deep_analyses_per_week=None,
            max_concurrent_streams=2,
            rag_enabled=True,
            patch_generation_enabled=True,
            memory_level="advanced",
            max_input_chars=8_000,
        ),
        PlanCode.PLUS: PlanEntitlements(
            requests_per_minute=40,
            ai_units_per_day=500,
            standard_requests_per_day=None,
            rag_requests_per_day=None,
            deep_analyses_per_week=None,
            max_concurrent_streams=3,
            rag_enabled=True,
            patch_generation_enabled=True,
            memory_level="advanced",
            max_input_chars=12_000,
        ),
        PlanCode.MAX: PlanEntitlements(
            requests_per_minute=80,
            ai_units_per_day=2_000,
            standard_requests_per_day=None,
            rag_requests_per_day=None,
            deep_analyses_per_week=None,
            max_concurrent_streams=5,
            rag_enabled=True,
            patch_generation_enabled=True,
            memory_level="advanced",
            max_input_chars=16_000,
        ),
    }
)

ROUTE_UNIT_COST: Mapping[InternalRoute, int] = MappingProxyType(
    {
        InternalRoute.SAFE_RESPONSE: 0,
        InternalRoute.DETERMINISTIC: 0,
        InternalRoute.ALFRED: 1,
        InternalRoute.RAG_THEN_ALFRED: 2,
        InternalRoute.FEEDBACKER: 3,
        InternalRoute.RAG_THEN_FEEDBACKER: 4,
    }
)


def get_plan_entitlements(plan_code: PlanCode | str) -> PlanEntitlements:
    """Return a known plan or fail closed for corrupted/unknown data."""

    try:
        normalized = PlanCode(plan_code)
        return PLAN_ENTITLEMENTS[normalized]
    except (ValueError, KeyError) as error:
        raise ValueError(f"Unsupported plan code: {plan_code}") from error


def get_route_unit_cost(route: InternalRoute | str) -> int:
    """Return the weighted cost of one concrete internal graph route."""

    try:
        normalized = InternalRoute(route)
        return ROUTE_UNIT_COST[normalized]
    except (ValueError, KeyError) as error:
        raise ValueError(f"Unsupported internal route: {route}") from error
