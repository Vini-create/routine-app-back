"""Stable values persisted by the internal billing system."""

from enum import StrEnum


class PlanCode(StrEnum):
    FREE = "free"
    PRO = "pro"
    PLUS = "plus"
    MAX = "max"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"


class BillingProviderCode(StrEnum):
    INTERNAL = "internal"
    STRIPE = "stripe"


class UsageEventStatus(StrEnum):
    RESERVED = "reserved"
    CONSUMED = "consumed"
    RELEASED = "released"
    FAILED = "failed"
