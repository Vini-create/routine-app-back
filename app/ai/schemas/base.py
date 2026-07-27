"""Shared Pydantic configuration for AI contracts."""

from pydantic import BaseModel, ConfigDict


class AISchema(BaseModel):
    """Strict base model that rejects undocumented fields."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        use_enum_values=False,
    )
