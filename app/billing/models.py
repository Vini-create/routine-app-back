"""Persistence model for plan ownership, independent from payment providers."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.billing.enums import (
    BillingProviderCode,
    PlanCode,
    SubscriptionStatus,
)
from app.db.db import Base
from app.models.models import TimestampMixin

if TYPE_CHECKING:
    from app.models.auth import User


class BillingAccount(Base, TimestampMixin):
    """Internal source of truth for a user's plan and subscription state."""

    __tablename__ = "billing_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    plan_code: Mapped[str] = mapped_column(
        String(30),
        default=PlanCode.FREE.value,
        server_default=PlanCode.FREE.value,
        nullable=False,
    )
    subscription_status: Mapped[str] = mapped_column(
        String(30),
        default=SubscriptionStatus.ACTIVE.value,
        server_default=SubscriptionStatus.ACTIVE.value,
        nullable=False,
    )
    billing_provider: Mapped[str] = mapped_column(
        String(30),
        default=BillingProviderCode.INTERNAL.value,
        server_default=BillingProviderCode.INTERNAL.value,
        nullable=False,
    )
    provider_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    provider_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="billing_account")

    __table_args__ = (
        CheckConstraint(
            "plan_code IN ('free', 'pro', 'plus', 'max')",
            name="ck_billing_accounts_plan_code",
        ),
        CheckConstraint(
            "subscription_status IN ('active', 'trialing', 'past_due', 'canceled')",
            name="ck_billing_accounts_subscription_status",
        ),
        CheckConstraint(
            "billing_provider IN ('internal', 'stripe')",
            name="ck_billing_accounts_provider",
        ),
        CheckConstraint(
            "current_period_end IS NULL OR current_period_start IS NULL "
            "OR current_period_end > current_period_start",
            name="ck_billing_accounts_period",
        ),
    )
