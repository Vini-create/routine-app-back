"""Contracts produced by input security and user-safety checks."""

from typing import Any

from pydantic import Field

from app.ai.domain.enums import SafetyLevel
from app.ai.schemas.base import AISchema


class SafetyAssessment(AISchema):
    level: SafetyLevel
    categories: list[str] = Field(default_factory=list, max_length=20)
    risk_score: float = Field(ge=0, le=1)
    blocked: bool = False
    prompt_injection_suspected: bool = False
    prompt_injection_score: float = Field(default=0, ge=0, le=1)
    prompt_injection_signals: list[str] = Field(default_factory=list, max_length=20)
    restrictions: list[str] = Field(default_factory=list, max_length=20)


class SafeResponse(AISchema):
    message: str = Field(min_length=1, max_length=4_000)
    category: str = Field(min_length=1, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)
