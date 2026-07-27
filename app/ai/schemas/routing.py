"""Structured output contracts for intent classification and routing."""

from pydantic import Field

from app.ai.domain.enums import InternalRoute
from app.ai.schemas.base import AISchema


class RoutingDecision(AISchema):
    detected_intent: str = Field(min_length=1, max_length=120)
    intent_confidence: float = Field(ge=0, le=1)
    route: InternalRoute
    route_confidence: float = Field(ge=0, le=1)
    route_reason: str = Field(min_length=1, max_length=500)
    required_context: list[str] = Field(default_factory=list, max_length=20)
