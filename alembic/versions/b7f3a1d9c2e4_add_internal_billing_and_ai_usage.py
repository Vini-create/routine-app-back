"""add internal billing accounts and auditable AI usage

Revision ID: b7f3a1d9c2e4
Revises: 7c85e2a5c931
Create Date: 2026-07-26 16:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b7f3a1d9c2e4"
down_revision: Union[str, Sequence[str], None] = "7c85e2a5c931"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "signature_plan",
        existing_type=sa.String(length=30),
        server_default="free",
        existing_nullable=False,
    )
    op.create_table(
        "billing_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "plan_code",
            sa.String(length=30),
            server_default="free",
            nullable=False,
        ),
        sa.Column(
            "subscription_status",
            sa.String(length=30),
            server_default="active",
            nullable=False,
        ),
        sa.Column(
            "billing_provider",
            sa.String(length=30),
            server_default="internal",
            nullable=False,
        ),
        sa.Column("provider_customer_id", sa.String(length=255), nullable=True),
        sa.Column("provider_subscription_id", sa.String(length=255), nullable=True),
        sa.Column(
            "current_period_start",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "current_period_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "billing_provider IN ('internal', 'stripe')",
            name="ck_billing_accounts_provider",
        ),
        sa.CheckConstraint(
            "current_period_end IS NULL OR current_period_start IS NULL "
            "OR current_period_end > current_period_start",
            name="ck_billing_accounts_period",
        ),
        sa.CheckConstraint(
            "plan_code IN ('free', 'pro', 'plus', 'max')",
            name="ck_billing_accounts_plan_code",
        ),
        sa.CheckConstraint(
            "subscription_status IN ('active', 'trialing', 'past_due', 'canceled')",
            name="ck_billing_accounts_subscription_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    # Product decision for this portfolio release: all existing accounts start
    # from the same free baseline, even if the legacy column contains another
    # value. No Stripe customer is created by this migration.
    op.execute("UPDATE users SET signature_plan = 'free'")
    op.execute(
        """
        INSERT INTO billing_accounts (
            id,
            user_id,
            plan_code,
            subscription_status,
            billing_provider,
            cancel_at_period_end
        )
        SELECT
            gen_random_uuid(),
            users.id,
            'free',
            'active',
            'internal',
            false
        FROM users
        ON CONFLICT (user_id) DO NOTHING
        """
    )

    op.create_table(
        "ai_usage_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=True),
        sa.Column("route", sa.String(length=40), nullable=False),
        sa.Column("plan_code", sa.String(length=30), nullable=False),
        sa.Column("reserved_units", sa.Integer(), nullable=False),
        sa.Column(
            "consumed_units",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "input_tokens",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "output_tokens",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "estimated_cost",
            sa.Numeric(precision=12, scale=6),
            server_default="0",
            nullable=False,
        ),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "is_stream",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "reservation_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "estimated_cost >= 0",
            name="ck_ai_usage_events_nonnegative_cost",
        ),
        sa.CheckConstraint(
            "reserved_units >= 0 AND consumed_units >= 0",
            name="ck_ai_usage_events_nonnegative_units",
        ),
        sa.CheckConstraint(
            "input_tokens >= 0 AND output_tokens >= 0",
            name="ck_ai_usage_events_nonnegative_tokens",
        ),
        sa.CheckConstraint(
            "plan_code IN ('free', 'pro', 'plus', 'max')",
            name="ck_ai_usage_events_plan_code",
        ),
        sa.CheckConstraint(
            "route IN ('safe_response', 'deterministic', 'alfred', "
            "'feedbacker', 'rag_then_alfred', 'rag_then_feedbacker')",
            name="ck_ai_usage_events_route",
        ),
        sa.CheckConstraint(
            "status IN ('reserved', 'consumed', 'released', 'failed')",
            name="ck_ai_usage_events_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_ai_usage_user_idempotency_key",
        ),
    )
    op.create_index(
        op.f("ix_ai_usage_events_user_id"),
        "ai_usage_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_usage_stream_reservations",
        "ai_usage_events",
        ["user_id", "is_stream", "status", "reservation_expires_at"],
        unique=False,
    )
    op.create_index(
        "ix_ai_usage_user_created_status",
        "ai_usage_events",
        ["user_id", "created_at", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ai_usage_user_created_status",
        table_name="ai_usage_events",
    )
    op.drop_index(
        "ix_ai_usage_stream_reservations",
        table_name="ai_usage_events",
    )
    op.drop_index(
        op.f("ix_ai_usage_events_user_id"),
        table_name="ai_usage_events",
    )
    op.drop_table("ai_usage_events")
    op.drop_table("billing_accounts")
    op.alter_column(
        "users",
        "signature_plan",
        existing_type=sa.String(length=30),
        server_default=None,
        existing_nullable=False,
    )
