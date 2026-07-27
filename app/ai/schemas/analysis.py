"""Structured contracts for Alfred's internal analytical capability."""

from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.ai.domain.limits import MAX_ROLLING_SUMMARY_CHARS
from app.ai.schemas.base import AISchema
from app.ai.schemas.patches import PatchOperation


class ExecutionDiagnosis(AISchema):
    summary: str = Field(min_length=1, max_length=2_000)
    data_window: str = Field(min_length=1, max_length=100)
    data_quality: float = Field(ge=0, le=1)
    observed_facts: list[str] = Field(default_factory=list, max_length=20)


class IdentifiedPattern(AISchema):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=1_000)
    evidence: list[str] = Field(default_factory=list, max_length=10)
    confidence: float = Field(ge=0, le=1)


class RootCauseHypothesis(AISchema):
    hypothesis: str = Field(min_length=1, max_length=1_000)
    supporting_evidence: list[str] = Field(default_factory=list, max_length=10)
    alternative_explanations: list[str] = Field(default_factory=list, max_length=10)
    confidence: float = Field(ge=0, le=1)
    sensitive: bool = False


class Recommendation(AISchema):
    priority: int = Field(ge=1, le=5)
    title: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=1, max_length=1_000)
    action: str = Field(min_length=1, max_length=1_000)


class SuccessMetric(AISchema):
    name: str = Field(min_length=1, max_length=150)
    baseline: float | int | str | None = None
    target: float | int | str
    evaluation_window_days: int = Field(ge=1, le=365)


class ModelPatchProposal(AISchema):
    """Strict LLM output; backend-only fields are added after validation."""

    entity_type: Literal["goal", "habit", "routine_item", "profile"]
    entity_id: UUID | None = None
    operations: list[PatchOperation] = Field(min_length=1, max_length=20)
    reason: str = Field(min_length=1, max_length=2_000)
    success_metrics: list[SuccessMetric] = Field(
        default_factory=list,
        max_length=10,
    )


class AnalysisReport(AISchema):
    diagnosis: ExecutionDiagnosis
    patterns: list[IdentifiedPattern] = Field(default_factory=list, max_length=20)
    hypotheses: list[RootCauseHypothesis] = Field(
        default_factory=list,
        max_length=10,
    )
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        max_length=5,
    )
    success_metrics: list[SuccessMetric] = Field(
        default_factory=list,
        max_length=10,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisSynthesis(AISchema):
    """Single structured model output shared by downstream analysis nodes."""

    hypotheses: list[RootCauseHypothesis] = Field(
        default_factory=list,
        max_length=10,
    )
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        max_length=5,
    )
    success_metrics: list[SuccessMetric] = Field(
        default_factory=list,
        max_length=10,
    )
    response_message: str = Field(min_length=1, max_length=6_000)
    proposed_patch: ModelPatchProposal | None = None
    updated_summary_en: str = Field(
        min_length=1,
        max_length=MAX_ROLLING_SUMMARY_CHARS,
    )
