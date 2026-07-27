import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    Time,
    DateTime,
    ForeignKey,
    func,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.models.models import TimestampMixin
from app.db.db import Base

if TYPE_CHECKING:
    from app.billing.models import BillingAccount
    from app.models.routine import CoachProfile, Goal, Habit, RoutineItem
    from app.models.ai import AIUsageEvent, ChatMessage, Feedback


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(80),
        default="America/Sao_Paulo",
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(30),
        default="english_us",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    signature_plan: Mapped[str] = mapped_column(
        String(30),
        default="free",
        server_default="free",
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    has_password: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    pending_deletion: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    credentials: Mapped[Optional["UserCredential"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    preferences: Mapped["UserPreference"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    coach_profiles: Mapped[list["CoachProfile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    habits: Mapped[list["Habit"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    routine_items: Mapped[list["RoutineItem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    feedbacks: Mapped[list["Feedback"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    billing_account: Mapped[Optional["BillingAccount"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    ai_usage_events: Mapped[list["AIUsageEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    auth_action_tokens: Mapped[list["AuthActionToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    external_identities: Mapped[list["ExternalIdentity"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    login_challenges: Mapped[list["LoginChallenge"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserCredential(Base, TimestampMixin):
    __tablename__ = "user_credentials"

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

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="credentials",
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"

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

    theme: Mapped[str] = mapped_column(
        String(20),
        default="system",
        nullable=False,
    )

    notification_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    reminder_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="preferences",
    )


class AuthActionToken(Base):
    __tablename__ = "auth_action_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    token_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="auth_action_tokens",
    )


class ExternalIdentity(Base, TimestampMixin):
    __tablename__ = "external_identities"
    __table_args__ = (
        UniqueConstraint(
            "provider", "subject", name="uq_external_identity_provider_subject"
        ),
        UniqueConstraint(
            "user_id", "provider", name="uq_external_identity_user_provider"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="external_identities")


class LoginChallenge(Base):
    __tablename__ = "login_challenges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    challenge_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    secret_hash: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="login_challenges")
