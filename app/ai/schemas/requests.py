"""Public request contracts for the single Alfred API."""

import json
from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from app.ai.domain.enums import SelectedSkill
from app.ai.schemas.base import AISchema

MAX_INPUT_CHARS = 4_000
MAX_SCREEN_CONTEXT_BYTES = 8_000


class AIInvokeRequest(AISchema):
    """Invoke any Alfred capability through one public contract."""

    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=MAX_INPUT_CHARS)
    selected_skill: SelectedSkill = SelectedSkill.AUTO
    screen_context: dict[str, Any] | None = None
    idempotency_key: UUID | None = None

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message cannot be blank")
        return value

    @field_validator("screen_context")
    @classmethod
    def limit_screen_context(
        cls,
        value: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if value is None:
            return None

        try:
            encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError) as error:
            raise ValueError("screen_context must be JSON serializable") from error

        if len(encoded.encode("utf-8")) > MAX_SCREEN_CONTEXT_BYTES:
            raise ValueError(
                f"screen_context cannot exceed {MAX_SCREEN_CONTEXT_BYTES} bytes"
            )
        return value
