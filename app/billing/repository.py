"""Database access for internal billing accounts."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.enums import (
    BillingProviderCode,
    PlanCode,
    SubscriptionStatus,
)
from app.billing.models import BillingAccount


def build_free_billing_account(user_id: UUID) -> BillingAccount:
    """Build the free account that must be persisted with a new user."""

    return BillingAccount(
        user_id=user_id,
        plan_code=PlanCode.FREE.value,
        subscription_status=SubscriptionStatus.ACTIVE.value,
        billing_provider=BillingProviderCode.INTERNAL.value,
        provider_customer_id=None,
        provider_subscription_id=None,
    )


async def get_billing_account(
    session: AsyncSession,
    user_id: UUID,
    *,
    for_update: bool = False,
) -> BillingAccount | None:
    statement = select(BillingAccount).where(BillingAccount.user_id == user_id)
    if for_update:
        statement = statement.with_for_update()
    result = await session.execute(statement)
    return result.scalar_one_or_none()
