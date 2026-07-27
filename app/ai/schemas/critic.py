"""Structured contract for the bounded output critic."""

from pydantic import Field, model_validator

from app.ai.schemas.base import AISchema


class CriticReview(AISchema):
    approved: bool
    issues: list[str] = Field(default_factory=list, max_length=8)
    revised_message: str | None = Field(default=None, max_length=6_000)

    @model_validator(mode="after")
    def require_revision_when_rejected(self) -> "CriticReview":
        if not self.approved and not self.revised_message:
            raise ValueError("A rejected output must include revised_message.")
        return self
