"""add bounded Feedbacker decision memory

Revision ID: e4b7c2d91a63
Revises: d9a6c4e81f20
Create Date: 2026-07-26 23:30:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e4b7c2d91a63"
down_revision: Union[str, Sequence[str], None] = "d9a6c4e81f20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_feedbacker_decision_memories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("patch_id", sa.UUID(), nullable=False),
        sa.Column("adjustment_type", sa.String(length=160), nullable=False),
        sa.Column("context", sa.Text(), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("inferred_preference", sa.Text(), nullable=False),
        sa.Column(
            "confidence",
            sa.Numeric(precision=4, scale=3),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_ai_feedbacker_decision_memory_confidence",
        ),
        sa.CheckConstraint(
            "decision IN ('accepted', 'rejected')",
            name="ck_ai_feedbacker_decision_memory_decision",
        ),
        sa.ForeignKeyConstraint(
            ["patch_id"],
            ["ai_proposed_patches.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patch_id"),
    )
    op.create_index(
        op.f("ix_ai_feedbacker_decision_memories_user_id"),
        "ai_feedbacker_decision_memories",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_feedbacker_memory_user_created",
        "ai_feedbacker_decision_memories",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ai_feedbacker_memory_user_created",
        table_name="ai_feedbacker_decision_memories",
    )
    op.drop_index(
        op.f("ix_ai_feedbacker_decision_memories_user_id"),
        table_name="ai_feedbacker_decision_memories",
    )
    op.drop_table("ai_feedbacker_decision_memories")
