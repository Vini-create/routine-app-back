"""add login challenges and google identities

Revision ID: 7c85e2a5c931
Revises: 40cce90a05fa
Create Date: 2026-07-03 18:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c85e2a5c931"
down_revision: Union[str, Sequence[str], None] = "40cce90a05fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "has_password", sa.Boolean(), server_default=sa.true(), nullable=False
        ),
    )
    op.create_table(
        "external_identities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider", "subject", name="uq_external_identity_provider_subject"
        ),
        sa.UniqueConstraint(
            "user_id", "provider", name="uq_external_identity_user_provider"
        ),
    )
    op.create_index(
        op.f("ix_external_identities_user_id"),
        "external_identities",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "login_challenges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("challenge_type", sa.String(length=30), nullable=False),
        sa.Column("secret_hash", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_login_challenges_challenge_type"),
        "login_challenges",
        ["challenge_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_login_challenges_user_id"),
        "login_challenges",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_login_challenges_user_id"), table_name="login_challenges")
    op.drop_index(
        op.f("ix_login_challenges_challenge_type"), table_name="login_challenges"
    )
    op.drop_table("login_challenges")
    op.drop_index(
        op.f("ix_external_identities_user_id"), table_name="external_identities"
    )
    op.drop_table("external_identities")
    op.drop_column("users", "has_password")
