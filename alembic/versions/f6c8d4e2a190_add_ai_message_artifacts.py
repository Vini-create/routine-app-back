"""persist structured Alfred artifacts in assistant messages

Revision ID: f6c8d4e2a190
Revises: e4b7c2d91a63
Create Date: 2026-07-27 12:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f6c8d4e2a190"
down_revision: Union[str, Sequence[str], None] = "e4b7c2d91a63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ai_messages",
        sa.Column(
            "analysis",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "ai_messages",
        sa.Column(
            "references",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "ai_messages",
        sa.Column(
            "proposed_patch",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "ai_messages",
        sa.Column("requires_confirmation", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "ai_messages",
        sa.Column("patch_status", sa.String(length=20), nullable=True),
    )
    op.create_check_constraint(
        "ck_ai_messages_patch_status",
        "ai_messages",
        "patch_status IS NULL OR "
        "patch_status IN ('pending', 'applied', 'rejected', 'expired')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_ai_messages_patch_status",
        "ai_messages",
        type_="check",
    )
    op.drop_column("ai_messages", "patch_status")
    op.drop_column("ai_messages", "requires_confirmation")
    op.drop_column("ai_messages", "proposed_patch")
    op.drop_column("ai_messages", "references")
    op.drop_column("ai_messages", "analysis")
