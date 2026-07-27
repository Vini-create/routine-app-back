"""Plan validation independent from Stripe and from the AI graph."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.domain.errors import AIApplicationError, AIErrorCode
from app.billing.entitlements import PlanEntitlements, get_plan_entitlements
from app.billing.enums import PlanCode, SubscriptionStatus
from app.billing.models import BillingAccount
from app.billing.repository import get_billing_account


@dataclass(frozen=True, slots=True)
class BillingAccess:
    account: BillingAccount
    plan_code: PlanCode
    entitlements: PlanEntitlements


async def require_active_billing_access(
    session: AsyncSession,
    user_id: UUID,
    *,
    for_update: bool = False,
    request_id: UUID | None = None,
) -> BillingAccess:
    """Fail closed unless the user owns a usable internal billing account."""

    account = await get_billing_account(session, user_id, for_update=for_update)
    if account is None:
        raise AIApplicationError(
            AIErrorCode.PLAN_UNAVAILABLE,
            "No billing account is available for this user",
            request_id=str(request_id) if request_id else None,
        )

    if account.subscription_status not in {
        SubscriptionStatus.ACTIVE.value,
        SubscriptionStatus.TRIALING.value,
    }:
        raise AIApplicationError(
            AIErrorCode.PLAN_UNAVAILABLE,
            "The current plan is not active",
            request_id=str(request_id) if request_id else None,
        )

    try:
        plan_code = PlanCode(account.plan_code)
        entitlements = get_plan_entitlements(plan_code)
    except ValueError as error:
        raise AIApplicationError(
            AIErrorCode.PLAN_UNAVAILABLE,
            "The billing account has an unsupported plan",
            request_id=str(request_id) if request_id else None,
        ) from error

    return BillingAccess(
        account=account,
        plan_code=plan_code,
        entitlements=entitlements,
    )
