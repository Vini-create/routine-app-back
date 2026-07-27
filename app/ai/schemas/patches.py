"""Contracts for suggestions that require explicit human confirmation."""

from typing import Any, Literal
from uuid import UUID

from pydantic import Field, field_validator

from app.ai.schemas.base import AISchema


class PatchOperation(AISchema):
    op: Literal["add", "remove", "replace"]
    path: str = Field(min_length=2, max_length=300)
    # Alfred patches only editable scalar columns. Nested objects would widen
    # the mutation surface and make schema validation ambiguous.
    value: str | int | float | bool | None = None

    @field_validator("path")
    @classmethod
    def validate_json_pointer(cls, value: str) -> str:
        if not value.startswith("/") or "//" in value:
            raise ValueError("path must be a valid absolute JSON pointer")
        return value


class ProposedPatch(AISchema):
    patch_id: UUID | None = None
    entity_type: Literal["goal", "habit", "routine_item", "profile"]
    entity_id: UUID | None = None
    operations: list[PatchOperation] = Field(min_length=1, max_length=20)
    reason: str = Field(min_length=1, max_length=2_000)
    simulation: dict[str, Any] | None = None
    success_metrics: list[dict[str, Any]] = Field(
        default_factory=list,
        max_length=10,
    )


class PatchAcceptRequest(AISchema):
    idempotency_key: UUID


class PatchRejectRequest(AISchema):
    reason: str | None = Field(default=None, max_length=500)


class PatchEditRequest(AISchema):
    idempotency_key: UUID
    operations: list[PatchOperation] = Field(min_length=1, max_length=20)
