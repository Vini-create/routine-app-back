"""Structured intermediate contracts for Alfred's conversational capability."""

from pydantic import Field

from app.ai.domain.limits import MAX_ROLLING_SUMMARY_CHARS
from app.ai.schemas.base import AISchema


class AlfredResponsePlan(AISchema):
    objective: str = Field(min_length=1, max_length=500)
    tone: str = Field(min_length=1, max_length=100)
    key_points: list[str] = Field(default_factory=list, max_length=8)
    next_steps: list[str] = Field(default_factory=list, max_length=5)
    should_ask_question: bool = False


class AlfredIntervention(AISchema):
    strategy: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=6_000)
    next_steps: list[str] = Field(default_factory=list, max_length=5)
    memory_candidates: list[str] = Field(default_factory=list, max_length=10)
    updated_summary_en: str = Field(
        min_length=1,
        max_length=MAX_ROLLING_SUMMARY_CHARS,
    )
