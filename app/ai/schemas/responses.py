"""Stable public response contracts for Alfred."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.ai.domain.enums import InternalRoute
from app.ai.schemas.analysis import AnalysisReport
from app.ai.schemas.base import AISchema
from app.ai.schemas.patches import ProposedPatch
from app.ai.schemas.retrieval import EvidenceReference


class AIUsage(AISchema):
    plan: str = Field(min_length=1, max_length=30)
    units_reserved: int = Field(ge=0)
    units_consumed: int = Field(ge=0)
    units_remaining: int | None = Field(default=None, ge=0)


class QuotaUsageResponse(AISchema):
    used: int = Field(ge=0)
    limit: int | None = Field(default=None, ge=0)
    remaining: int | None = Field(default=None, ge=0)
    reset_at: datetime


class AIUsageResponse(AISchema):
    plan: str
    weighted_units_today: QuotaUsageResponse
    standard_requests_today: QuotaUsageResponse
    rag_requests_today: QuotaUsageResponse
    deep_analyses_this_week: QuotaUsageResponse
    requests_per_minute: int = Field(ge=1)


class AICapabilitiesResponse(AISchema):
    plan: str
    capabilities: dict[str, bool | str]


class AIInvokeResponse(AISchema):
    request_id: UUID
    conversation_id: UUID
    route: InternalRoute
    message: str = Field(min_length=1, max_length=12_000)
    references: list[EvidenceReference] = Field(
        default_factory=list,
        max_length=12,
    )
    analysis: AnalysisReport | None = None
    proposed_patch: ProposedPatch | None = None
    requires_confirmation: bool = False
    usage: AIUsage

    @model_validator(mode="after")
    def keep_patch_confirmation_consistent(self) -> "AIInvokeResponse":
        has_patch = self.proposed_patch is not None
        if has_patch != self.requires_confirmation:
            raise ValueError(
                "proposed_patch and requires_confirmation must be set together"
            )
        if self.proposed_patch is not None and self.proposed_patch.patch_id is None:
            raise ValueError("a public proposed_patch must have a persisted patch_id")
        return self


class AIErrorResponse(AISchema):
    request_id: UUID
    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1_000)
    details: dict[str, Any] = Field(default_factory=dict)


class AIConversationCreate(AISchema):
    title: str = Field(default="Nova conversa", min_length=1, max_length=160)


class AIConversationSummary(AISchema):
    id: UUID
    title: str
    summary_en: str | None = None
    created_at: datetime
    updated_at: datetime


class AIMessageResponse(AISchema):
    id: UUID
    role: Literal["user", "assistant", "system"]
    content: str
    route: InternalRoute | None = None
    analysis: AnalysisReport | None = None
    references: list[EvidenceReference] | None = Field(
        default=None,
        max_length=12,
    )
    proposed_patch: ProposedPatch | None = None
    requires_confirmation: bool | None = None
    patch_status: Literal["pending", "applied", "rejected", "expired"] | None = (
        None
    )
    request_id: UUID
    created_at: datetime


class AIConversationDetail(AIConversationSummary):
    messages: list[AIMessageResponse]


class PatchResolutionResponse(AISchema):
    patch_id: UUID
    status: Literal["pending", "applied", "rejected", "expired"]
    proposed_patch: ProposedPatch
    audit_id: UUID | None = None
    requires_confirmation: bool
