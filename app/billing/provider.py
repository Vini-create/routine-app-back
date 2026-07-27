"""Provider boundary that keeps Stripe outside the AI graph."""

from dataclasses import dataclass
from typing import Protocol

from app.billing.enums import PlanCode, SubscriptionStatus
from app.models.auth import User


class BillingProviderError(RuntimeError):
    """Raised when a provider cannot execute a requested operation."""


@dataclass(frozen=True, slots=True)
class BillingWebhookEvent:
    """Provider-neutral result produced only after signature verification."""

    event_id: str
    event_type: str
    customer_id: str
    subscription_id: str | None
    plan_code: PlanCode | None
    subscription_status: SubscriptionStatus | None


class BillingProvider(Protocol):
    async def create_customer(self, user: User) -> str: ...

    async def create_checkout_session(
        self,
        *,
        user: User,
        plan_code: PlanCode,
    ) -> str: ...

    async def create_customer_portal(self, customer_id: str) -> str: ...

    async def parse_webhook(
        self,
        *,
        payload: bytes,
        signature: str,
    ) -> BillingWebhookEvent: ...


class InternalBillingProvider:
    """Free-only provider; it never creates external billing resources."""

    async def create_customer(self, user: User) -> str:
        raise BillingProviderError(
            "The internal provider does not create external customers"
        )

    async def create_checkout_session(
        self,
        *,
        user: User,
        plan_code: PlanCode,
    ) -> str:
        raise BillingProviderError(
            "Paid checkout is not available through the internal provider"
        )

    async def create_customer_portal(self, customer_id: str) -> str:
        raise BillingProviderError(
            "The internal provider does not expose a customer portal"
        )

    async def parse_webhook(
        self,
        *,
        payload: bytes,
        signature: str,
    ) -> BillingWebhookEvent:
        del payload, signature
        raise BillingProviderError(
            "The internal provider does not receive payment webhooks"
        )
