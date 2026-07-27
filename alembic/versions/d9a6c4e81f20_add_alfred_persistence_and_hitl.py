"""add Alfred persistence, memory and human-in-the-loop tables

Revision ID: d9a6c4e81f20
Revises: b7f3a1d9c2e4
Create Date: 2026-07-26 21:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d9a6c4e81f20"
down_revision: Union[str, Sequence[str], None] = "b7f3a1d9c2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("summary_en", sa.Text(), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_conversations_user_id"),
        "ai_conversations",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_conversations_user_updated",
        "ai_conversations",
        ["user_id", "updated_at"],
        unique=False,
    )

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("detected_language", sa.String(length=20), nullable=True),
        sa.Column("route", sa.String(length=40), nullable=True),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="ck_ai_messages_role",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["ai_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "request_id",
            "role",
            name="uq_ai_messages_request_role",
        ),
    )
    op.create_index(
        op.f("ix_ai_messages_conversation_id"),
        "ai_messages",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_messages_request_id"),
        "ai_messages",
        ["request_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_messages_user_id"),
        "ai_messages",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_messages_conversation_created",
        "ai_messages",
        ["conversation_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "ai_proposed_patches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=True),
        sa.Column("operations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("simulation", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "success_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("resolution_idempotency_key", sa.UUID(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "entity_type IN ('goal', 'habit', 'routine_item', 'profile')",
            name="ck_ai_proposed_patches_entity_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'applied', 'rejected', 'expired')",
            name="ck_ai_proposed_patches_status",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["ai_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        op.f("ix_ai_proposed_patches_conversation_id"),
        "ai_proposed_patches",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_proposed_patches_user_id"),
        "ai_proposed_patches",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_patches_user_status_expires",
        "ai_proposed_patches",
        ["user_id", "status", "expires_at"],
        unique=False,
    )

    op.create_table(
        "ai_patch_audit",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patch_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column(
            "before_state",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "after_state",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "rollback_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["patch_id"],
            ["ai_proposed_patches.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_patch_audit_patch_id"),
        "ai_patch_audit",
        ["patch_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_patch_audit_user_id"),
        "ai_patch_audit",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "ai_memories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=True),
        sa.Column("memory_type", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("importance", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("source_request_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
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
            "confidence >= 0 AND confidence <= 1 "
            "AND importance >= 0 AND importance <= 1",
            name="ck_ai_memories_scores",
        ),
        sa.CheckConstraint(
            "memory_type IN ('short_term', 'episodic', 'semantic')",
            name="ck_ai_memories_type",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["ai_conversations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "content_fingerprint",
            name="uq_ai_memories_user_fingerprint",
        ),
    )
    op.create_index(
        "ix_ai_memories_user_expires",
        "ai_memories",
        ["user_id", "expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_memories_user_id"),
        "ai_memories",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "ai_interventions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("intervention_type", sa.String(length=40), nullable=False),
        sa.Column(
            "before_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "expected_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("evaluation_due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "after_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("outcome", sa.String(length=30), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(
        op.f("ix_ai_interventions_user_id"),
        "ai_interventions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "ai_graph_checkpoints",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
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
            "status IN ('completed', 'pending_confirmation', 'resolved', 'failed')",
            name="ck_ai_graph_checkpoints_status",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["ai_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_ai_checkpoints_user_idempotency",
        ),
    )
    op.create_index(
        op.f("ix_ai_graph_checkpoints_conversation_id"),
        "ai_graph_checkpoints",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_graph_checkpoints_user_id"),
        "ai_graph_checkpoints",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_checkpoints_user_status_expires",
        "ai_graph_checkpoints",
        ["user_id", "status", "expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ai_checkpoints_user_status_expires",
        table_name="ai_graph_checkpoints",
    )
    op.drop_index(
        op.f("ix_ai_graph_checkpoints_user_id"),
        table_name="ai_graph_checkpoints",
    )
    op.drop_index(
        op.f("ix_ai_graph_checkpoints_conversation_id"),
        table_name="ai_graph_checkpoints",
    )
    op.drop_table("ai_graph_checkpoints")
    op.drop_index(
        op.f("ix_ai_interventions_user_id"),
        table_name="ai_interventions",
    )
    op.drop_table("ai_interventions")
    op.drop_index("ix_ai_memories_user_expires", table_name="ai_memories")
    op.drop_index(op.f("ix_ai_memories_user_id"), table_name="ai_memories")
    op.drop_table("ai_memories")
    op.drop_index(op.f("ix_ai_patch_audit_user_id"), table_name="ai_patch_audit")
    op.drop_index(op.f("ix_ai_patch_audit_patch_id"), table_name="ai_patch_audit")
    op.drop_table("ai_patch_audit")
    op.drop_index(
        "ix_ai_patches_user_status_expires",
        table_name="ai_proposed_patches",
    )
    op.drop_index(
        op.f("ix_ai_proposed_patches_user_id"),
        table_name="ai_proposed_patches",
    )
    op.drop_index(
        op.f("ix_ai_proposed_patches_conversation_id"),
        table_name="ai_proposed_patches",
    )
    op.drop_table("ai_proposed_patches")
    op.drop_index(
        "ix_ai_messages_conversation_created",
        table_name="ai_messages",
    )
    op.drop_index(op.f("ix_ai_messages_user_id"), table_name="ai_messages")
    op.drop_index(op.f("ix_ai_messages_request_id"), table_name="ai_messages")
    op.drop_index(
        op.f("ix_ai_messages_conversation_id"),
        table_name="ai_messages",
    )
    op.drop_table("ai_messages")
    op.drop_index(
        "ix_ai_conversations_user_updated",
        table_name="ai_conversations",
    )
    op.drop_index(
        op.f("ix_ai_conversations_user_id"),
        table_name="ai_conversations",
    )
    op.drop_table("ai_conversations")
